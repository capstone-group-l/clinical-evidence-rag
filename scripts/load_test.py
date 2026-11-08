import json
import os
import subprocess
import sys
import tempfile

URL = "http://localhost:8000/v1/query"
QUESTION = """What is the first-line treatment for
uncomplicated iron deficiency anemia in women?"""
USERS = 50


def main():

    # Set up temporary json file for the payload for Fortio
    payload_file = tempfile.NamedTemporaryFile(
        delete=False, suffix=".json", mode="w", encoding="utf-8"
    )
    json.dump({"question": QUESTION}, payload_file)
    payload_file.close()

    out_file = tempfile.mktemp(suffix=".json")

    try:
        print(f"Started Load Test of {USERS} concurrent users...")

        # -c sets concurrent connections, and -n sets total requests.
        load_cmd = [
            "fortio",
            "load",
            "-c",
            str(USERS),
            "-n",
            str(USERS),
            "-qps",
            "0",
            "-p",
            "50,95",
            "-timeout",
            "35s",
            "-json",
            out_file,
            "-content-type",
            "application/json",
            "-payload-file",
            payload_file.name,
            "-X",
            "POST",
            URL,
        ]

        try:
            res = subprocess.run(load_cmd, capture_output=True, text=True)
        except FileNotFoundError:
            sys.exit("Error: Couldn't find fortio executable")

        if res.returncode != 0 and not os.path.exists(out_file):
            sys.exit("Fortio failed to run")

        # Parse JSON results
        with open(out_file, "r", encoding="utf-8") as f:
            result = json.load(f)

        percentile = {}
        for item in result["DurationHistogram"]["Percentiles"]:
            percentile_key = str(item["Percentile"])
            percentile[percentile_key] = item["Value"]

        http_responses = result.get("RetCodes", {})

        total_requests = 0
        successful_requests = 0

        for status_code, count in http_responses.items():
            total_requests += count

            # Counts succesful return codes received.
            if str(status_code).startswith("2"):
                successful_requests += count

            # Calculates how many requests failed
            errors = total_requests - successful_requests

            # Calculate the error percentage
            if total_requests > 0:
                error_rate = (errors / total_requests) * 100
            else:
                error_rate = 100

            # Get the 95th percentile time
            p95_time = percentile.get("95", 30)

            # Get the slowest request time
            slowest = result["DurationHistogram"]["Max"]

            # Checks if the target is met (95th percentile < 30s and no errors)
            if errors == 0 and p95_time < 30:
                target_passed = True
            else:
                target_passed = False

        # Test Results
        print("\n--- Load Test Results ---")
        print(f"Requests: {total_requests}")
        print(f"Concurrent simulated users: {USERS}")
        print(f"Errors: {errors}")
        print(f"Error Rate: {error_rate:.2f}%")
        print(f"Slowest Request Time: {slowest:.2f}s")
        print(f"95th Percentile: {p95_time:.2f}s")
        if target_passed:
            print("Target Met (95th percentile < 30s): PASS")
        else:
            print("Target Met (95th percentile < 30s): FAIL")

        if not target_passed:
            sys.exit(1)

    finally:
        for temp_f in [payload_file.name, out_file]:
            if os.path.exists(temp_f):
                os.remove(temp_f)


if __name__ == "__main__":
    main()
