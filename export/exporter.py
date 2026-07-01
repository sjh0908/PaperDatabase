import csv
import io
import json

def rows_to_csv(rows):
    output = io.StringIO()

    if not rows:
        return "\ufeff"

    fieldnames = rows[0].keys()

    writer = csv.DictWriter(output, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(rows)

    return "\ufeff" + output.getvalue()


def rows_to_json(rows):
    return json.dumps(
        rows,
        ensure_ascii=False,
        indent=4,
        default=str
    )