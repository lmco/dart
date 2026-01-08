<!--
# Copyright 2026 Lockheed Martin Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
-->

# Offline Installation Guide for DART

## Requirements

- admin rights
- git/zip file
- python >=3.8
- pip >=20.0

---

## Setup local installation

Goal – Install DART on a machine that has no internet access. All Python packages are pre‑downloaded on a separate, internet‑enabled workstation and then transferred to the isolated host.
Result – DART runs locally at http://localhost:<PORT> (the default port is 8000 unless you change it in settings.py).

---

### Part A – Prepare the Offline Package Repository (Internet‑Enabled Machine)

1. Clone / copy the DART source tree

   ```
   # Choose any location you like, e.g. ~/dart‑src
   git clone https://github.com/lockheedmartin/dart.git /path/to/DART
   # OR copy an existing ZIP/tarball and extract it
   ```

1. Create a local “wheelhouse” with all dependencies

   ```
   # Create a folder that will hold the downloaded wheels
   mkdir -p offline_packages

   # Download every package (including transitive deps) into that folder
   python3 -m pip download -r requirements.txt -d offline_packages
   ```

   > _The command above works on Linux/macOS as well as Windows (use python -m pip if python3 is not on the PATH)._

1. Verify the wheelhouse (optional but recommended)

   ```
   # Quick sanity check – list the files
   ls offline_packages | wc -l   # should be > 0
   # Or on Windows:
   dir offline_packages
   ```

---

### Part B – Transfer Files to the Isolated Machine

1. Copy the entire **DART** source directory and the **offline_packages** folder to the target system.

   > _**Important**: Preserve the directory structure. After the copy you should have something like:_

   ```
   /DART/
   │   manage.py
   │   requirements.txt
   │   …
   └─ offline_packages/
       aiohttp‑3.8.5‑py3-none-any.whl
       python_docx‑0.8.11‑py3-none-any.whl
       …
   ```

### Part C – Install DART on the Isolated Machine

> Assumption: The DART root directory on the offline host is /DART. Change all paths below if you placed the project elsewhere.

1. Create a dedicated virtual environment

   ```
   cd /DART
   python3 -m venv .dart-env
   ```

   > _The environment will be created in the hidden folder .dart-env inside the project root._

1. Activate the virtual environment

   | OS                   | Command                          |
   | -------------------- | -------------------------------- |
   | Linux / macOS        | source .dart-env/bin/activate    |
   | Windows (PowerShell) | .\.dart-env\Scripts\Activate.ps1 |
   | Windows (cmd.exe)    | .\.\Scripts\activate.bat         |

   > After activation you should see the prompt prefixed with (.dart-env).

1. Install all requirements from the local wheelhouse

   ```
   python -m pip install --no-index --find-links=offline_packages -r requirements.txt
   ```

   - `no-index` prevents pip from trying to query PyPI.
   - `find-links=offline_packages` tells pip to look only in that folder for wheels / source tarballs.

1. Verify the installation (optional)

   ```
   python - <<'PY'
   import django, docx, pkg_resources, sys
   print('Django version:', django.get_version())
   print('python-docx version:', pkg_resources.get_distribution('python-docx').version)
   print('Python executable:', sys.executable)
   PY
   ```

   > You should see the versions printed without errors.

---

### Part D – Run DART

    ```
    # From the /DART directory (virtualenv must be active)
    python manage.py runserver 0.0.0.0:<PORT>
    ```

    Replace `<PORT>` with the port you want DART to listen on (default is 8000).

    You can now reach the application from the same machine via:
    ```
    http://localhost:`<PORT>`
    ```

    If the host has a firewall, be sure to allow inbound traffic on that port.

---

### Troubleshooting Checklist

| Symptom                                                            | Likely cause                                                | Fix                                                             |
| ------------------------------------------------------------------ | ----------------------------------------------------------- | --------------------------------------------------------------- |
| `pip: command not found`                                           | Virtualenv not activated or Python not on `PATH`            | Re‑activate the venv or add Python to `PATH`.                   |
| `Error: Could not find a version that satisfies the requirement …` | Missing wheel in `offline_packages`                         | Re‑run the download step on the online machine and re‑transfer. |
| `ImportError: No module named 'django'`                            | Packages not installed in the venv                          | Run the `pip install …` command again while the venv is active. |
| `Permission denied` when running the installer on Windows          | Not running as Administrator                                | Open a Command Prompt / PowerShell with Run as administrator.   |
| Application starts but returns 404 for static files                | `collectstatic` not executed (if using production settings) | Run `python manage.py collectstatic` before `runserver`.        |


### Summary Flow Diagram

```
Online Machine
 ├─ Update requirements.txt
 ├─ pip download -r requirements.txt -d offline_packages
 └─ Copy /DART + offline_packages → Offline Machine

Offline Machine
 ├─ Install Python 3 (if needed)
 ├─ python3 -m venv .dart-env
 ├─ source .dart-env/bin/activate
 ├─ pip install --no-index --find-links=offline_packages -r requirements.txt
 └─ python manage.py runserver 0.0.0.0:<PORT>
```

### Quick Reference Commands (copy‑paste)

```
# ---------- ONLINE ----------
cd /path/to/DART
sed -i 's/^python-docx.*$/python-docx>=0.8.11/' requirements.txt   # Linux/macOS
# Windows PowerShell alternative:
# (Get-Content requirements.txt) -replace '^python-docx.*$', 'python-docx>=0.8.11' | Set-Content requirements.txt
python3 -m pip download -r requirements.txt -d offline_packages
```

```
# ---------- OFFLINE ----------
cd /DART
python3 -m venv .dart-env
source .dart-env/bin/activate      # or the Windows equivalent
python -m pip install --no-index --find-links=offline_packages -r requirements.txt
python manage.py runserver 0.0.0.0:8000
```