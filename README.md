# OSINT Google Dork Generator

This project is an **interactive Python tool for OSINT investigations**, designed to
generate Google Dorks based on different types of targets:

- Email addresses  
- Usernames / aliases  
- Domains  
- Subdomains  

The tool includes:

✅ Interactive menu  
✅ Colorama-based CLI (colored terminal)  
✅ Automatic export to `.txt`  
✅ Specialized Dorks for each target type  
✅ Clean and modular code  

---

## 🚀 Features

### 🔍 Target Types Supported
You can generate OSINT-focused Google Dorks for:

- **Email** (example: `john@example.com`)  
- **Username** (example: `johnny99`)  
- **Domain** (example: `example.com`)  
- **Subdomain** (example: `dev.example.com`)  

Each option generates a unique set of targeted Dorks:
documents, leaks, exposed directories, social media, archives, and more.

---

## 📦 Requirements

The only external library used is:

```

colorama

````

Install it with:

```bash
pip install colorama
````

---

## ▶️ Usage

Run the script:

```bash
python dork_generator.py
```

Then follow the interactive menu:

1. Choose the target type
2. Enter the value (email, username, domain…)
3. View the generated Dorks
4. Optionally export them to a `.txt` file

Example export file name:

```
dorks_john_example_com.txt
```

---

## 📁 Project Structure

```
│── dork_generator.py    # Main script
│── README.md            # Documentation
│── .gitignore           # macOS + Python ignores
```

---

## 🛡️ Ethical Disclaimer

This tool is intended **solely for legitimate OSINT research**, cybersecurity training,
defensive analysis, and educational purposes.

Do not use it for unauthorized access, harassment, or any illegal activity.

---

## 🤝 Contributions

Feel free to submit pull requests, suggestions, or new Dork categories.
All contributions are welcome!

---