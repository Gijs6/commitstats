# CommitStats

Python script for extracting Git commit stats. It calculates the total number of lines changed across all commits per day

## Output Format

```json
{
    "2025-03-17": {
        "value": 20,
        "repos": {
            "Other": 5,
            "gijs6.nl": 2,
            "school.gijs6.nl": 13
        }
    },
    "2025-03-12": {
        "value": 15,
        "repos": {
            "Other": 2,
            "CKVsite": 3,
            "school.gijs6.nl": 10
        }
    }
}
```

## Usage

These scripts extract the raw data from Git repositories. For heatmap visualization examples, see [gijs6.nl repo](https://github.com/Gijs6/gijs6.nl).
