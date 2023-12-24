def string_with_arrows(text, pos_start, pos_end):
    result = ""

    # Calculate indices
    idx_start = max(text.rfind("\n", 0, pos_start.idx), 0)
    idx_end = text.find("\n", idx_start + 1)
    if idx_end < 0:
        idx_end = len(text)

    # Generate each ln
    ln_count = pos_end.ln - pos_start.ln + 1
    for i in range(ln_count):
        # Calculate ln columns
        ln = text[idx_start:idx_end]
        col_start = pos_start.col if i == 0 else 0
        col_end = pos_end.col if i == ln_count - 1 else len(ln) - 1

        # Append to result
        result += ln + "\n"
        result += " " * col_start + "^" * (col_end - col_start)

        # Re-calculate indices
        idx_start = idx_end
        idx_end = text.find("\n", idx_start + 1)
        if idx_end < 0:
            idx_end = len(text)

    return result.replace("\t", "")
