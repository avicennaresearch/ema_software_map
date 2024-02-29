# EMA Software Comparison
Ecological Momentary Assessment, or EMA, is a software widely used by
researchers in health research and pscyhology to collect real-world data from
participants. Researchers use EMA software to study humans throughout their
daily lives, rather than in a lab. So it's important for the software to be as
invisible as possible. It should get activated exactly when needed, ask a few
short questions, collect necessary sensor and wearable data, decide whether an
intervention should be prompted, and disappear until next time.

At its core, EMAs are a very simple software: they prompt a notification to the
participant, ask them to complete a short survey or interact with an
intervention, and then upload the data. That's one reason there are so many of
it. We are aware of 63!

But it's not easy to pick the right software. The main reason is, even though
the EMA software plays a deceiveingly simple role, if it fails, it can
jeoperdize the entire study. For example, if the software fails to notify
participants when it's time to answer a quick survey, no data will be collected
and the entire study is destroyed.

Another reason is EMAs, unlike business-focus softwares, require more
flexibility to conform to the study design. So often studies have quite a
few additional requirements aside from short surveys. This includes intervention
management, cognitive task features, tele-visit and communication features,
simplified enrollment, screening, consent, onboarding, and so on. At the same time,
the research often has limited budget to allocate to the software.

When you combine the above with the large number of available software, and their
poor to non-existent documentation of them, you will realize selecting an EMA software
is like marriage. You have to make a huge decision with very limited information,
and the consequence of that decision can even make or break your research career.

The purpose of this repository is gather as much information as possible about
software packages, and document pros and cons of each of them.

# Methodology
## References
The data presented in this repository are collected from publicly accessible
records.


The [reference.csv](reference.csv) file contains all URLs we have included to be
monitored visited for this repo. The file contains the following:
 * `id`: The neumerical ID of the reference.
 * `software`: The software package name.
 * `url`: The URL.
 * `last_visited`: Last time our software visited this URL.
 * `status`: The status. It can be either :
   * `Active`: the site could be reached.
   * `Inactive`: the site was not accessible.

## Algorithm
1. We start with the package name, say Beiwe.
2. Do a comprehensive search to find all base URLs for this product, e.g.
   1. beiwe.org
   2. https://github.com/onnela-lab/beiwe-backend/wiki
   3. https://github.com/onnela-lab/beiwe-ios/wiki
   4. https://github.com/onnela-lab/Beiwe-Analysis/wiki/
   5. https://forest.beiwe.org/en/latest/
3. Run `scrapy site_generator` to extract all webpages
4. Add each site to a db:
   1. ID
   2. package_name
   3. URL
   4. last_modified -> defaults to None. If less than now, it will be set manually, if more than now, it will be set automatically when a change is detected.
   5. is_monitored -> whether it's being monitoring right now by changedetection. Defaults to False.
5. A service also adds this URL to change detection.
6. It also reads the content, toeknizes it, and places them into a database.

# Software Packages
Software Name, # of Marketing Pages, # of Technical Pages, Freshness, Last Checked
Beiwe,

We have done our best to make sure we cover any public information available
from any software package. But this is not a trivial task. We used technology
to simplify the work, but there is a risk that we might have missed something.
For example, maybe the crawler has missed part of your website completely, and
therefore the content of your package is not properly presented.

If that's the case, please contact us and we will correct the code.

# Contribution
TBD

# Technical Details
To install this software:

1. Install pyenv
2. Configure python to use python 3.11:
   1. `pyenv install 3.11`
   2. `pyenv shell 3.11`
3. Install virtual env: `python -m venv .venv`
4. Activate the venv `source .venv/bin/activate`
5. Install poetry: `pip3 install poetry`
6. Install all dependencies: `poetry install`
We are using an array of software packages to achieve this task, some are listed
below:

1. Django: As a web interface for this project.
2. Scrapy: To scrape the websites
3. ChangeDetection: To monitor the websites and detect changes as they occur.

## Installing Django


# Contact
Mohammad Hashemian

# License
TBD

# Policies
## Exclusion
The information in this repository are complied only using publicly accessible
data. Therefore we do not exclude them.
If you are the maintainer of any of these software packages and prefer to be
excluded from this list, you can block our IP address (142.112.79.25) so our bot
cannot read your website anymore. Although, the information we have collected so
far will remain in the list.

# Resources
1. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10619650/
2. https://en.wikipedia.org/wiki/Mobile_phone_based_sensing_software
3. https://docs.google.com/spreadsheets/d/18R9x9Qbl9tADJGpJBJID_T9EWZeQ_4W3OFdn3iKRU7U/edit#gid=204277638
