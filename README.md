For summary of this repo, check the following spreadsheet:

[Access Here](https://docs.google.com/spreadsheets/d/1zRuZIJKE9mm90asM9U07MRmoJE51giFEUMJQhXZDf3Y/edit#gid=1750024108)

# Why EMA Software Map?

There are many EMA softwares out there. This makes it very difficult to choose
the right software for a new research. There has been some work like 
[this] or [this] to help researchers choose wisely, but they all are either too
abstract, or too dated, or incomplete.

At Avicenna, we have been monitoring EMA softwares for some time. This helps
us to know what is our differentiator, and where we fall short. We have tried to
do this systematically and with an unbiased perspective, so we get the right
feedback, even if the result something we want to hear. 

In this repository, we are open-sourcing our research results. Our goal of doing
so is two-fold: first, we hope the content here can help other researchers also
to make more informed decisions in choosing the right software for their
research. Second, we hope researchers contribute and feedback what areas require
more attention and development, and this way shape the way EMA software are being
developed.

# How to Read This File

To check the EMA software feature map, please open
[this spreadsheet](https://docs.google.com/spreadsheets/d/1zRuZIJKE9mm90asM9U07MRmoJE51giFEUMJQhXZDf3Y/edit#gid=1750024108).
The sheet is divided into a set of sections, and each section is further divided
into a set of subsections. Each subsection then lists a set of features that a
software package may offer in full, partially offer it, or not offer it at all.
Therefore, each row either shows a section, a subsection, or a feature.

Each row starts with an ID, which is assigned sequentially. The second column in
each row is either the section or subsection title, or the feature description.
Following the `Row ID` and `Feature Name` columns, companies are listed
alphabetically. Each company has two rows: `Coverage` and `Notes`.

For feature rows, the `Coverage` column is one of the following:

- `Supported`: the software supports 75% or more of that feature.
- `Partial Support`: the software supports between 25% to 75% of that feature.
- `Not Supported`: the software does not support the feature, or supports less
  than 25% of it.

For section and subsection rows, the `Coverage` column shows to what percent that
category is supported by this software.

The `Notes` column is empty for section and subsection rows. But for feature
rows, this column rationale behind the assigned coverage or assessment, if needed.

The sections, subsections, and columns are grouped so it's easier to navigate in
the file.

You only have read-only access to this file. That means you cannot collapse or
expand the main spreadsheet file either (Google Sheets limitation). To do so,
simply create a copy of the file and play with it as you like.

# Methodology

To perform this analysis, we selected softwares that:

1. Their main purpose are EMA and health research.
2. Have public documentation. Ideally, they also allow us to create test
   accounts.
3. Are being actively maintained (i.e. at least one update in the past 6
   months).

For each software, we read the documentation in detail and listed their
features. Then we mapped the features to our feature hierarchy as closely as
possible. If a feature did not exist, we added a new entry and evaluated that
feature in other already-reviewed platforms to make sure it's not missed.

We defined a feature as a capability that can be understood by researchers, as
opposed to being very technical, and brings clear value to their research.

As reviewing the documentation of a product, we divided our notes into two
categories:

- Subjective Assessment: this is our impression from working with the product.
  Basically what we thought was the strength and what is the weakness of this
  product. We wrote this in an accompanying blog post.
- Objective Qualifications: basically, what features are offered and what
  features are not. These are added to this repository and are used for
  calculating the feature coverage.

We write our subjective assessment as a blog post in our website. We cannot
prove or disprove our statements there. So you may want to take it with a grain
of salt. But our Objective Assessments are shared in this repo. We welcome
public contribution to it and happily modify it if we have missed anything.

# Technical Details

Ideally, this work would be just a simple spreadsheet file. But then the
contribution to it would be difficult. Spreadsheets are not the best to track
changes, provide reasoning for those changes, and discuss the reasons.

GitHub is perfect for such versioning and discussions, but it's not easy to view
the results. So we decided to have the data in GitHub, and automatically create
a spreadsheet to view the results.

Also, we did not want this to be a one-time effort. We want this feature map
table to remain up-to-date as the software packages change. So we also needed
an automated monitoring system.

The above reasons are why we created this repository the way it is. You can read
more for its technical details.

## Underlying JSON File

The underlying data are stored in a JSON file. The file has an array
of sections, each containing an array of sub-sections, and each in turn
containing an array of features. If you are familiar with JSON, it should be
fairly easy to read it. Any change to this file triggers the update script
at `scripts/process_json.py`. The script does the following:

1. Deletes the old sheet.
2. Creates a new sheet using the values in this JSON.
3. Applies the formatting: cell colors, frozen rows and columns, % format of the
   coverage cells, grouping of rows and columns, and so on.
4. Updates the formula of coverage cells based on the row IDs.

This method allows us to work on the JSON file to discuss the changes, but
always have the sheet as an easy way to see the results.

## Change Monitoring

We use [ChangeDetection](https://github.com/dgtlmoon/changedetection.io) to
monitor the changes to any software packages we have reviewed. During the review
process, we create a list of all URLs we visited. The list is stored in a text
file under the `sitemaps` directory. Then we add all of these URLs to the
ChangeDetection to be checked every other day. If any changes, we get an email
and update the content of the JSON file, which in turn will update the sheet.

This way the sheet will remain up-to-date all the time.

# Who can contribute? How to Contribute?

Anyone can contribute. In fact, we have gone out of our way to make sure
everyone can contribute to this, all contributions are traceable, and any
decision is documented. This way, we can be sure that no matter who contributes,
the bias will be minimal.

## Contribution Criteria

To further minimize the bias and increase the validity of this table, we have
defined the following conditions.

### Only Actively Maintained Products

We define actively maintained products as those that have been updated within
the past 6 months. If a product we have documented stops receiving updates we
move it to a deprecated space and slowly phase it out.

### Only Products with Public Documentation

We only include products that have public documentation. Ideally, the product
allows us to create an account and test it too. This helps more accurate
representation. But that's not mandatory.

### Only Documented Features and Capabilities

We only rely on the documentation, and if available, the actual product, to
evaluate what features exist and how they work. During our review, we do our
best to remove all marketing-oriented content and focus purely on the features
being offered.

### Only Features Related to EMA & Health Research Software

Some softwares offer features that, while valuable, have no use in health
research. Examples include features that are for care delivery or patient
monitoring. Also, some companies offer hardware products along with software. We
exclude all these. The focus of this repository is features related to health
research software and EMAs.

Note that we include EMI, JITAI, digital phenotyping, and other closely-relevant
topics.

## How Can I Change Something?

Just open a [pull request](https://docs.github.com/articles/about-pull-requests)
with the change you want to make.

In that pull request, please make sure you provide documentation to support the
change you are making. This can be either in the related `Notes` column or as
part of the PR's commit message.

If you are referring to a new URL, please specify that so we can include it in
our ChangeDetection.

# FAQ

## Why Software XYZ is not covered?

If the software fits [our criteria](#Contribution-Criteria), and it's not in
[our roadmap](#Roadmap) yet, please add it to the roadmap.

## Something is not correct in the document.

Please open a pull request and update it. Make sure you check the
[steps to contribute](#Who-can-contribute-How-to-Contribute) first.

## I own software XYZ, and I don't want to be included in this.

Please block our IP address (142.112.79.25), so we cannot access your content
anymore.
