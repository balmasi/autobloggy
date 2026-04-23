# Layout Integrity

Screenshots are bundled for multiple viewport widths (typically 360 px mobile and 820 px prose column). Evaluate **every** width supplied in the instructions, not just one.

Pass only if, at every provided width: all text is fully visible — no words or characters clipped by container boundaries, no content overflowing outside its parent element, no horizontal page scrollbar, and no element running off the right edge of the viewport. Fail if any text is partially hidden, truncated by overflow, or cut off at the edge of a card or container at any width. A visual that looks fine at 820 px but clips or overflows at 360 px fails.
