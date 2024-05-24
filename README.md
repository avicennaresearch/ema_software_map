Spreadsheet to Compare Available EMA Softwares.

[Access Here](https://docs.google.com/spreadsheets/d/1zRuZIJKE9mm90asM9U07MRmoJE51giFEUMJQhXZDf3Y/edit#gid=1750024108)

# Why EMA Comparison?

There are many EMA softwares out there. Some were released just a year ago while
others have been gathering dust for more than 10 years. Some offer lots of free
features, while others don't give you the option to even see the product unless
you go through a sales process!

This makes it very difficult to choose a software for a new research. Most
researchers just pick a software they've heard before, do some due diligence and
if nothing smells, purchase a license and move on to their research. They just
hope nothing breaks. This is far from perfect. Some feel buyer's remorse as soon
as they start implementing their protocol. Especially when things get hard
during the field deployment, they start thinking maybe there was a more suitable
option out there.

At Avicenna, we have been monitoring our competitors for some time. This helps
us to know what is our differentiator, and where we fall short. We have tried to
do this systematically and with an unbiased perspective, so we get the right
feedback, even if it's bitter or not something we want to hear. We believe this
can help other researchers as well in deciding as to which software they should
choose.

In this repository, we are open-sourcing our competitive landscape research. We
hope the content here can help other researchers also to make more informed
decisions in choosing the right software for their research.

# How to Read This File

To check the comparison, please open
[this spreadsheet](https://docs.google.com/spreadsheets/d/1zRuZIJKE9mm90asM9U07MRmoJE51giFEUMJQhXZDf3Y/edit#gid=1750024108).
The sheet is divided into a set of sections, and each section is further divided
into a set of subsections. Each subsection then lists a set of features that a
software package may offer in full, partially offer it, or not offer it at all.
Therefore, each row either shows a section, a subsection, or a feature.

Each row starts with an ID, which is assigned sequentially. The second column in
each row is either the section or subsection title, or the feature description.
Following the `Row ID` and `Feature Name` columns, companies are listed
alphabetically. Each company has two rows: `Score` and `Notes`.

For feature rows, the `Score` column is one of the following:

- `Supported`: the software supports 75% or more of that feature.
- `Partial Support`: the software supports between 25% to 75% of that feature.
- `Not Supported`: the software does not support the feature, or supports less
  than 25% of it.

For section and subsection rows, the `Score` column shows to what percent that
category is supported by this software.

The `Notes` column is empty for section and subsection rows. But for feature
rows, this column rationale behind the assigned score or assessment, if needed.

The sections, subsections, and columns are grouped so it's easier to navigate in
the file.

You only have read-only access to this file. That means you cannot collapse or
expand the main spreadsheet file either (Google Sheets limitation). To do so,
simply create a copy of the file and play with it as you like.

# Roadmap

We are going to add the following softwares to the list as well:

1. mEMA
2. ExpiWell
3. Biewe
4. Fibion
5. mindLAMP
6. myCap
7. NeuroUX
8. RealLife Exp
9. TIIM
10. Ksana Health

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

We share the results of both here. Please note the distinction when reading the
content. The table here is objectively measured, we welcome public contribution
to it and happily modify it if we have missed an item or two. On the other hand,
the blog posts are our personal assessment of the software, and we cannot prove
it one way or the other. So you may want to take it with a grain of salt.

# Technical Details

Ideally, this comparison would be just a simple spreadsheet file. But then the
contribution to it would be difficult. Spreadsheets are not the best to track
changes, provide reasoning for those changes, and discuss the reasons.

GitHub is perfect for such versioning and discussions, but it's not easy to view
the results. So we decided to have the data in GitHub, and automatically create
a spreadsheet to view the results.

Also, we did not want this to be a one-time effort. We want the comparison table
to remain up-to-date as the software packages change. So we also needed an
automated monitoring system.

The above reasons are why we created this repository the way it is. You can read
more for its technical details.

## Underlying JSON File

The underlying comparison data are stored in a JSON file. The file has an array
of rows: one element per each row of the sheet. Any change to this file triggers
the update script at `scripts/process_json.py`. The script does the following:

1. Deletes the old sheet.
2. Creates a new sheet using the values in this JSON.
3. Applies the formatting: cell colors, frozen rows and columns, % format of the
   score cells, grouping of rows and columns, and so on.
4. Updates the formula of score cells based on the row IDs.

This method allows us to work on the JSON file to discuss the changes and
comparisons, but always have the sheet as an easy way to see the results.

## Change Monitoring

We use [ChangeDetection](https://github.com/dgtlmoon/changedetection.io) to
monitor the changes to any software packages we have reviewed. During the review
process, we create a list of all URLs we visited. The list is stored in a text
file under the `sitemaps` directory. Then we add all of these URLs to the
ChangeDetection to be checked every other day. If any changes, we get an email
and update the content of the comparison JSON file, which in turn will update
the sheet.

This way the sheet will remain up-to-date all the time.

# Who can contribute? How to Contribute?

Anyone can contribute. In fact, we have gone out of our way to make sure
everyone can contribute to this, all contributions are traceable, and any
decision is documented. This way, we can be sure that no matter who contributes,
the bias will be minimal.

## Contribution Criteria

To further minimize the bias and increase the validity of this comparison table,
we have defined the following conditions.

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
