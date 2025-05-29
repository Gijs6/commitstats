# CommitStats

Some scripts that get the Git commit frequency so you can use it on a gh-like heatmap or whatever

`GetCommitDates.py` just returns the total number of commits for each day and the total commits per repo per day.

`GetCommitLines.py` gets the total number of lines changed in all commits on a day.

This is how the outputted data looks for both repos (the values will differ between the scripts of course)  

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
    },
    ...
}
```

This code is just to get the data from git, the code that I use for generating the heatmap on my own site is visible on [the repo of my site :D](https://github.com/Gijs6/gijs6.nl)
