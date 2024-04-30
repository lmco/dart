# DART: A Documentation and Reporting Tool

DART is a test documentation tool created by the Lockheed Martin Red Team to
document and report on penetration tests, especially in isolated network environments. 

# This works with python 3.9

The goals of this tool are:

- __Easy__
  - Quick to set up without internet connectivity
  - No extensive configuration required
- __Enabling__
  - Maximize testing time; minimize reporting time
  - Apply NISPOM-friendly portion markings
  - Capture test artifacts
- __Expendable__
  - You won't lose sleep over leaving the tool behind to be destroyed
  - The report and artifacts files contain everything needed from the test

## Full Disclosure Regarding Security

DART is intended to be executed in isolated, uncontested environments such as an 
isolan, private test network, or on a standalone machine. It is _not_ 
intended for deployment on untrusted networks.

## Output Examples

### Multiple mission support

![Multiple mission support](examples/mission-list.png?raw=true "Multiple mission support")

### Test case & artifact tracking

![Test case & artifact tracking](examples/tests-list.png?raw=true "Test case & artifact tracking")

### Generates a Microsoft Word report 

![Generates a Microsoft Word report](examples/output-testcase-with-finding.png?raw=true "Generates a Microsoft Word report")

## Getting Started

### Supported Configurations 

DART is tested to work in the following configurations:

- Windows
- Linux
- Mac
- Docker

Other configurations will likely be successful, however we do not 
currently test DART's operation in these configurations.

### Installation

- [Local install instructions](docs/local-setup.md)
- [Docker install instructions](docs/docker-setup.md)

## Frequently Asked Questions

### Does everyone need their own account?

- Since this is a tool intended to be used by a team during an active and organic penetration test with many moving
parts, we typically just use a single-mission username and password that the execution team knows. RBAC is _not_ implemented
in this tool today.

### What are some dangerous actions I should avoid?

- Multiple people editing test case details / mission details will likely result in
  data loss. The last person to save a details page wins and __only__ their edits will
  be persisted. To help avoid this problem, see the question below.

#### How can I know if someone else is editing a test case?

- As soon as you begin working on a test case, change the status to "In Work" and Save.
  This will prompt others if they click on a test case you're currently working in
  so they know to check to see if the case has been saved. We usually use the POC field
  to know who to ask if they're still working the test case.

### Are there any export compliance concerns?

- Dependencies required by this tool may contain Export Controlled Information. Prior to
  building this tool outside the U.S. you should review the dependencies for any export
  compliance issues. Additionally, upon entering data into this tool the database file,
  supporting documentation folder, and outputs should be treated as sensitive, and
  handled as export controlled / classified information, as appropriate.


&copy; 2024 Lockheed Martin Corporation
