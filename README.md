# CareerXChange

A reproducible, self-contained starter template for using OpenAI APIs with both Node.js and Python.

This is for all members to refer to when setting up in their machines to do this SWESWE5008 practice module.

---

## 📦 Prerequisites

Install the following in case you are wondering what is missing in your system:

* Visual Studio Code
* Git
* Node.js (v18+ recommended, v20 preferred)
* Python (3.10+ recommended)
* Docker Desktop (optional but recommended)

Please create an OpenAI API key before proceeding (https://platform.openai.com/).
Please create an account at https://developer.ssg-wsg.gov.sg/webapp/home and create an app to obtain the CLIENT_ID and CLIENT_SECRET

---

## 🚀 1. Create Project

If you wish to recreate the base project, go through the following:


```bash
mkdir openai-starter
cd openai-starter
git init
code .
```

---

## 🗂️ 2. Project Structure

How our project is structured:

```
openai-starter/
├── node/
│   ├── package.json
│   └── index.js
│
├── python/
│   ├── app.py
│   └── requirements.txt
│
├── .env
├── .gitignore
├── docker-compose.yml
└── README.md
```

---

## 🔐 3. Environment Variables

Create `.env` in the root:

```
OPENAI_API_KEY=your_api_key_here
CLIENT_ID=your_ssg_client_id_here
CLIENT_SECRET=your_ssg_client_secret_here
```

Create `.gitignore`:

```
.env
node_modules/
__pycache__/
.venv/
```

---

## 🟩 4. Node.js Setup

### 4.1 Initialize project

```bash
cd node
npm init -y
npm install openai dotenv
```

### 4.2 Configure `package.json`

Ensure it looks like:

```json
{
  "name": "node",
  "version": "1.0.0",
  "main": "index.js",
  "type": "module",
  "scripts": {
    "start": "node index.js"
  },
  "dependencies": {
    "dotenv": "^16.0.0",
    "openai": "^4.0.0"
  }
}
```

---

### 4.3 Create `index.js`

```javascript
import OpenAI from "openai";
import dotenv from "dotenv";

// Load .env from project root
dotenv.config({ path: "../.env" });

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

async function main() {
  const response = await client.responses.create({
    model: "gpt-4.1-mini",
    input: "Explain event-driven architecture in one paragraph."
  });

  console.log(response.output[0].content[0].text);
}

main();
```

---

### 4.4 Run Node app

```bash
npm start
```

---

## 🐍 5. Python Setup

### 5.1 Create virtual environment

```bash
cd ../python
python -m venv .venv
```

Activate:

* macOS/Linux:

  ```bash
  source .venv/bin/activate
  ```
* Windows:

  ```powershell
  .venv\\Scripts\\activate
  ```

---

### 5.2 Install dependencies

```bash
pip install openai python-dotenv requests
pip freeze > requirements.txt
```

---

### 5.3 Create `app.py`

```python
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv("../.env")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.responses.create(
    model="gpt-4.1-mini",
    input="Explain microservices vs monolith briefly."
)

print(response.output[0].content[0].text)
```

---

### 5.4 Run Python app

```bash
python app.py
```

---

## 🐳 6. Docker (Optional but Recommended)

### 6.1 Create `docker-compose.yml`

```yaml
services:
  node:
    image: node:20
    working_dir: /app
    volumes:
      - ./node:/app
    env_file:
      - .env
    command: sh -c "npm install && node index.js"

  python:
    image: python:3.11
    working_dir: /app
    volumes:
      - ./python:/app
    env_file:
      - .env
    command: sh -c "pip install -r requirements.txt && python app.py"
```

---

### 6.2 Run all services

```bash
docker compose up
```

---

## 🔍 7. Troubleshooting

### ❌ Error: Missing credentials

```
OpenAIError: Missing credentials
```

**Fix:**

* Ensure `.env` exists at project root
* Ensure correct format:

  ```
  OPENAI_API_KEY=sk-xxxx
  ```
* Ensure correct loading path:

  * Node: `dotenv.config({ path: "../.env" })`
  * Python: `load_dotenv("../.env")`

---

### ❌ API key is undefined

Add debug:

```javascript
console.log(process.env.OPENAI_API_KEY);
```

If `undefined`, your `.env` is not being loaded correctly.

---

### ❌ JSON errors in package.json

* Ensure commas are correct
* Do not duplicate `scripts`
* Ensure valid JSON format

---

### ❌ Node import errors

Ensure:

```
"type": "module"
```

Or switch to CommonJS (`require`) if needed.

---

## ✅ 8. Verification Checklist

* Node app runs successfully
* Python app runs successfully
* API key is correctly loaded
* Docker setup works (optional)

---

## 📄 License

MIT (or your preferred license)
