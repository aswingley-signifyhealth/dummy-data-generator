import random
import string


def generate_medicaid_id(state_code: str) -> str:
    """
    Generates a random Medicaid ID string for the given two-letter state code,
    following the format rules in your table.
    """

    # Helper sets for convenience
    DIGITS = string.digits
    LETTERS = string.ascii_uppercase
    ALNUM = LETTERS + DIGITS

    def random_digit():
        return random.choice(DIGITS)

    def random_letter():
        return random.choice(LETTERS)

    def random_alnum():
        return random.choice(ALNUM)

    # Builds a random string given a single "format specification" dictionary.
    def build_id(fmt) -> str:
        length = fmt["length"]

        # "type" can be "digits" or "alnum".
        #  - "digits": all characters must be digits
        #  - "alnum": any char can be letter or digit,
        #    but we might have forced positions or "must_include_digit"/"must_include_letter"
        is_digits_only = (fmt["type"] == "digits")

        # Some states have positions that must be a *specific character*,
        # e.g. ND -> first two chars are "N" and "D", or WA -> last two are "W" "A".
        forced_chars = fmt.get("force_chars", {})
        # Some states have positions that must be a *letter* (but not necessarily the same one),
        # e.g. CO -> first character is always a letter, or CA -> 9th character is always letter.
        forced_types = fmt.get("force_type", {})

        must_include_digit = fmt.get("must_include_digit", False)
        must_include_letter = fmt.get("must_include_letter", False)

        # Start by building a list of placeholders
        result = [None] * length

        # Step 1: fill in forced *exact* characters
        for pos, ch in forced_chars.items():
            result[pos] = ch

        # Step 2: fill in forced letter positions (where we only know it must be a letter)
        for pos, t in forced_types.items():
            if t == "letter":
                # Only fill if not already forced by forced_chars
                if result[pos] is None:
                    result[pos] = random_letter()

        # Step 3: fill in all other positions with either digits or alnum
        for i in range(length):
            if result[i] is not None:
                continue  # already forced
            if is_digits_only:
                result[i] = random_digit()
            else:
                # we will assign alnum for now; later we'll enforce "must include digit/letter"
                result[i] = random_alnum()

        # If this format requires at least one digit and at least one letter,
        # we may need to re-roll until we satisfy that constraint
        if not is_digits_only and (must_include_digit or must_include_letter):
            # function to see if we have at least one digit and at least one letter
            def has_digit_and_letter(arr):
                has_dig = any(c.isdigit() for c in arr)
                has_let = any(c.isalpha() for c in arr)
                return has_dig, has_let

            # Because we may have forced letters at some positions, we only need
            # to check what's still missing and re-roll random positions if needed.
            # We'll do this in a simple while loop (usually it should be satisfied quickly).
            while True:
                has_dig, has_let = has_digit_and_letter(result)
                if (must_include_digit and not has_dig) or (must_include_letter and not has_let):
                    # randomly replace one character with a digit/letter to fix the deficiency
                    if must_include_digit and not has_dig:
                        # pick a random position (not forced) and make it a digit
                        idx_candidates = [i for i in range(length)
                                          if not (i in forced_chars or i in forced_types)]
                        if idx_candidates:
                            idx = random.choice(idx_candidates)
                            result[idx] = random_digit()

                    if must_include_letter and not has_let:
                        idx_candidates = [i for i in range(length)
                                          if not (i in forced_chars and i in forced_types)]
                        if idx_candidates:
                            idx = random.choice(idx_candidates)
                            result[idx] = random_letter()
                else:
                    break  # we have both required types now

        return "".join(result)

    

    # Look up the list of format specs for this state
    if not is_supported_state(state_code):
        raise ValueError(f"Unsupported or unknown state code: {state_code}")

    possible_formats = get_possible_formats_for_state(state_code)

    # If there is more than one format for a given state (e.g. CA), pick one at random
    fmt_choice = random.choice(possible_formats)

    # Build and return the result
    return build_id(fmt_choice)


def get_possible_formats() -> dict[str, list[dict]]:
    """
    # ------------------------------------------------------------
    # Dictionary of possible format(s) per state
    # ------------------------------------------------------------
    """
    state_formats = {
        # 10 digits
        "AK": [ {"length": 10, "type": "digits"} ],
        # 13 digits
        "AL": [ {"length": 13, "type": "digits"} ],
        "AR": [ {"length": 10, "type": "digits"} ],
        # 9 chars (letter+digits), first char forced to 'A'
        "AZ": [ {
            "length": 9,
            "type": "alnum",
            "force_chars": {0: "A"},
            "must_include_digit": True  # we already have one letter 'A'
        }],
        # CA has 2 formats:
        #   (1) 14 alnum, 9th char is letter
        #   (2)  9 alnum, 9th char is letter
        # Both must contain at least one letter+digit overall
        "CA": [
            {
                "length": 14,
                "type": "alnum",
                "force_type": {8: "letter"},  # 9th char => index=8
                "must_include_digit": True,
                "must_include_letter": True
            },
            {
                "length": 9,
                "type": "alnum",
                "force_type": {8: "letter"},
                "must_include_digit": True,
                "must_include_letter": True
            }
        ],
        # 7 chars, both letter+digit, 1st char forced letter
        "CO": [ {
            "length": 7,
            "type": "alnum",
            "force_type": {0: "letter"},
            "must_include_digit": True,
            "must_include_letter": True
        } ],
        "CT": [ {"length": 9, "type": "digits"} ],
        "DC": [ {"length": 8, "type": "digits"} ],
        "DE": [ {"length": 10, "type": "digits"} ],
        "FL": [ {"length": 10, "type": "digits"} ],
        "GA": [ {"length": 12, "type": "digits"} ],
        # 10 chars, 2nd char is forced letter
        "HI": [ {
            "length": 10,
            "type": "alnum",
            "force_type": {1: "letter"},
            "must_include_digit": True,
            "must_include_letter": True
        } ],
        # 8 chars, 1st char letter
        "IA": [ {
            "length": 8,
            "type": "alnum",
            "force_type": {0: "letter"},
            "must_include_digit": True,
            "must_include_letter": True
        } ],
        "ID": [ {"length": 10, "type": "digits"} ],
        "IL": [ {"length": 9, "type": "digits"} ],
        "IN": [ {"length": 12, "type": "digits"} ],
        "KY": [ {"length": 10, "type": "digits"} ],
        "KS": [ {"length": 10, "type": "digits"} ],
        "LA": [ {"length": 13, "type": "digits"} ],
        # Some states (like ME, MI) not in table => omitted
        "MA": [ {"length": 10, "type": "digits"} ],
        "MD": [ {"length": 11, "type": "digits"} ],
        "MN": [ {"length": 10, "type": "digits"} ],
        "MO": [ {"length": 8, "type": "digits"} ],
        "MS": [ {"length": 9, "type": "digits"} ],
        "MT": [ {"length": 7, "type": "digits"} ],
        # 10 chars, 10th char forced letter
        "NC": [ {
            "length": 10,
            "type": "alnum",
            "force_type": {9: "letter"},
            "must_include_digit": True,
            "must_include_letter": True
        } ],
        # 9 chars, first two forced 'N' 'D'
        "ND": [ {
            "length": 9,
            "type": "alnum",
            "force_chars": {0: "N", 1: "D"},
            "must_include_digit": True
            # already have 2 letters
        } ],
        "NE": [ {"length": 10, "type": "digits"} ],
        "NH": [ {"length": 10, "type": "digits"} ],
        "NJ": [ {"length": 12, "type": "digits"} ],
        "NM": [ {"length": 14, "type": "digits"} ],
        "NV": [ {"length": 11, "type": "digits"} ],
        # 8 chars, 1st,2nd,8th forced letter
        "NY": [ {
            "length": 8,
            "type": "alnum",
            "force_type": {0: "letter", 1: "letter", 7: "letter"},
            "must_include_digit": True
        } ],
        "OH": [ {"length": 12, "type": "digits"} ],
        "OK": [ {"length": 9,  "type": "digits"} ],
        # 8 chars, positions 1,2,6,8 forced letter => indexes 0,1,5,7 in 0-based
        "OR": [ {
            "length": 8,
            "type": "alnum",
            "force_type": {0: "letter", 1: "letter", 5: "letter", 7: "letter"},
            "must_include_digit": True
        } ],
        "PA": [ {"length": 10, "type": "digits"} ],
        "SC": [ {"length": 10, "type": "digits"} ],
        "SD": [ {"length": 9,  "type": "digits"} ],
        # 11 chars, first two forced "T","D"
        "TN": [ {
            "length": 11,
            "type": "alnum",
            "force_chars": {0: "T", 1: "D"},
            "must_include_digit": True
        } ],
        "TX": [ {"length": 9,  "type": "digits"} ],
        "UT": [ {"length": 10, "type": "digits"} ],
        "VA": [ {"length": 12, "type": "digits"} ],
        "VT": [ {"length": 7,  "type": "digits"} ],
        # 11 chars, last two forced "W","A"
        "WA": [ {
            "length": 11,
            "type": "alnum",
            "force_chars": {9: "W", 10: "A"},
            "must_include_digit": True
        } ],
        "WI": [ {"length": 10, "type": "digits"} ],
        "WV": [ {"length": 11, "type": "digits"} ],
        "WY": [ {"length": 10, "type": "digits"} ],
    }
    return state_formats
    
def get_supported_states() -> list[str]:
    state_formats = get_possible_formats()
    return list(state_formats.keys())
def is_supported_state(state_code: str) -> bool:
    return state_code in get_possible_formats()

def get_possible_formats_for_state(state: str) -> list[dict]:
    state_formats = get_possible_formats()
    return state_formats[state]