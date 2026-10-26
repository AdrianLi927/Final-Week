# How stiff is each gel? — README

Copy this file to `README.md` and fill in every section. No name anywhere: submission is anonymous.

## 1. The data, read by eye

For each experiment: the machine, the order of the columns, the units of force and area as stored, and the number you multiply each by to get N and m².

| experiment | machine | columns | force unit | × to get N | area unit | × to get m² |
|---|---|---|---|---|---|---|
| T01 | | | | | | |
| T02 | | | | | | |
| T03 | | | | | | |
| G.. (your choice) | | | | | | |
| G.. | | | | | | |
| G.. | | | | | | |

## 2. My decisions

- **Smoothing**: which filter, from which package, and what `width_points` means for it.
- **The width I trust**, and why: what you saw on your noisy digital curve at different widths (the E you got for each).
- Anything else that changes the answer and was not fixed by FINAL.md.

## 3. What the assistant decided that I had not asked for

In the bodies it wrote: choices you did not specify, and whether you kept them.

## 4. Diagnosis log

Every failure you met: what happened, which kind it was (the specification, the call, the body, the file, the environment), and what you changed. At least three entries.

| what happened | kind | what I changed |
|---|---|---|
| | | |

## 5. Results

The output of `python main.py`, pasted as it is:

```
```

## 6. How stable is the answer?

A short paragraph: how much do the averages change with the width? Is that change larger or smaller than the spread (±) within each type? Does the order of the four gels change? Which numbers would you report, and how many digits of them do you trust?

## 7. The clean rebuild

The outputs of `python -m pip install -r requirements.txt` (the last line), `python -m pytest` and `python main.py` in a new, empty folder (your zip, plus the `data/` folder of the starting pack):

```
```
