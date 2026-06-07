# Password Generator

A **Tkinter-based desktop password manager** for generating secure passwords, storing encrypted credentials, and managing password history. Powered by **PBKDF2-HMAC-SHA256**, **Fernet encryption**, and Python's **secrets** module, PasswordGuard provides a clean, modern, and secure local password management experience.

## Project Layout

The application automatically creates the required user and vault files when accounts are registered.

```markdown
> assets/
>    auth/
>       auth_dialog.py
>
>    pages/
>       generator_page.py
>       vault_page.py
>       history_page.py
>
>    app.py
>    theme.py
>    widgets.py
>
> src/
>    crypto.py
>    generator.py
>    utils.py
>
> main.py
>
> users.json
> vault_<username>.db
```

The application will generate `users.json` and encrypted user vault files automatically. Do not manually modify encrypted vault files.

## Quickstart

1. Create and activate a virtual environment

```bash
python -m venv .venv
```

For Linux or Mac:

```bash
source .venv/bin/activate
```

For Windows:

```bash
.venv\Scripts\activate
```

2. Install dependencies

```bash
pip install cryptography pyperclip
```

or

```bash
pip install -r requirements.txt
```

3. Run the Application

```bash
python main.py
```

OR

Run the file name:
```bash
Run_Application.cmd
```
To Automatically Run the Program.

Once started, the authentication dialog will appear and allow you to create an account or sign in to an existing vault.

## Objective

* Generate cryptographically secure passwords.
* Store credentials in encrypted local vaults.
* Protect user data using strong encryption practices.
* Maintain encrypted password generation history.
* Support multiple user accounts on a single installation.
* Provide a clean and intuitive desktop experience.

## Security

* Password-based authentication using PBKDF2-HMAC-SHA256.
* 390,000 PBKDF2 iterations for key derivation.
* Random 32-byte salts for password hashing and encryption keys.
* Fernet encryption for credential and history protection.
* Separate encrypted vault for each registered user.
* Cryptographically secure password generation using Python's `secrets` module.

## Architecture

* Authentication System → Account creation, login, and user switching.
* Password Generator → Secure password generation with configurable options.
* Credential Vault → Encrypted storage for websites, usernames, and passwords.
* Password History → Encrypted archive of generated passwords.
* UI Components → Reusable widgets, cards, buttons, and themed controls.
* Encryption Layer → Handles key derivation, encryption, decryption, and vault management.

## Highlights

* Modern dark-themed interface built with Tkinter.
* Multi-user support with independent encrypted vaults.
* Password strength analysis and entropy calculation.
* Clipboard integration for quick credential usage.
* Modular codebase with clear separation of UI and business logic.
* Local-first design with no cloud dependency.
* Lightweight and easy to run on any system with Python installed.

## Key Features

* Secure Authentication → Master password protected accounts.
* Password Generator → Generate strong passwords with customizable settings.
* Entropy Meter → View password strength and entropy estimates.
* Encrypted Vault → Securely store login credentials.
* Password History → Save and manage previously generated passwords.
* User Switching → Switch between multiple local accounts.
* Clipboard Support → Copy passwords instantly.
* Responsive UI Components → Consistent themed widgets throughout the application.

## Technologies Used

* Python
* Tkinter
* Cryptography
* Pyperclip
* PBKDF2-HMAC-SHA256
* Fernet Encryption
