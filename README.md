# DART: A Documentation and Reporting Tool

DART is a test documentation tool created by the Lockheed Martin Red Team to
document and report on penetration tests, especially in isolated network environments. 

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

- Windows 7 system install
- Docker (Experimental, read the warning in the Dockerfile)

Other configurations will likely be successful, however we do not 
currently test DART's operation in these configurations.

The installation instructions are comprised of two steps - a dependency collection 
step performed on an internet-connected machine and an installation step performed 
on the isolated network.

### Installing on Windows 7 (system-wide)

_On an internet-connected machine:_

- Online system must meet the following requirements for automated scripts to work:
  - Python 2.7 must be already installed (`python --version` to check)
  - **pip version must be > 9.0** (`pip --version` to check; `pip install -U pip` to update)

- Clone the repo & get the dependencies

```
git clone https://github.com/lmco/dart.git
cd dart
python install\online\prep.py
```

> **Note:** Some command line options, like `--proxy` are supported for your convenience. Use `python install\online\prep.py --help` for more info.

- Copy to offline machine

_On the isolated machine:_

- Offline system must meet the following requirements for automated scripts to work:
  - You must have administrative credentials (required for python installation)

- Install the dependencies

```
cd dart
install\offline\install.bat
```

- First Run Setup

```
python install\offline\setup.py
```

Basic DART installation and database creation is now complete. In addition you've 
loaded in common classification colors, a basic classification list, and some common
business areas you may have.

> **PRO TIP** If you have additional classifications or business areas in your 
> company, you can create a additional private entries for internal use
> by adding them (following the existing format) to the files in dart/missions/fixtures.

### Starting DART

```
python run.py
```

### Stopping DART

```
<CTRL+C>
```

## Connecting to DART

- Localhost: `127.0.0.1:8000`
- LAN: `<server_ip_address>:8000`

## Performing a version upgrade

- With the exception of the following files / locations, replace all DART files (copy and pasting the whole folder should be fine)
  - db.sqlite
  - SUPPORTING\_DATA\_PACKAGE/
  - supporting_data/
- Run the following commands

```
cd dart
python manage.py migrate
```

- Start DART normally

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

&copy; 2017 Lockheed Martin Corporation
