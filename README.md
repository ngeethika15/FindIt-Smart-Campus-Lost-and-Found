# 🔎 FindIt – Smart Campus Lost & Found

**One campus. One community. Helping lost belongings find their way home.**

FindIt is a smart campus Lost & Found Management System designed to help students report lost and found belongings, discover potential matches, and manage item recovery through a centralized platform.

## 🌐 Live Application

[Open FindIt – Live Demo](https://findit-smart-campus-lost-and-found-eebpkgjddlbny4p8dryway.streamlit.app/)

## ✨ Key Features

- **Student Authentication:** Registration and login functionality.
- **Report Lost or Found Items:** Submit item details, descriptions, locations, and images.
- **Browse Reports:** Search and filter reported items.
- **Smart Matching:** Compare item details to identify potentially matching lost and found reports.
- **Match Explanation:** Display similarity scores and explain how matches are evaluated.
- **Claim Management:** Submit, approve, or reject item recovery requests.
- **Recovery Tracking:** Update item status when belongings are recovered.
- **Demo Mode:** Explore the application using clearly labelled sample reports.

## 🧠 Smart Matching Methodology

FindIt uses a weighted similarity-based matching approach to identify potentially related lost and found reports.

The matching score considers:

| Matching factor | Weight |
|---|---:|
| Category match | 30 |
| Item name similarity | 25 |
| Description similarity | 25 |
| Colour match | 10 |
| Location similarity | 10 |
| **Total** | **100** |

Text similarity is calculated using Python's `SequenceMatcher`.

The resulting score is used to classify potential matches as Strong, Moderate, or Low.

*Note: Similarity scores are heuristic indicators, not probabilities or proof of ownership.*

## 🛠️ Technologies Used

- Python
- Streamlit
- SQLite
- Pandas
- Scikit-learn
- Pillow
- Git and GitHub

## 📁 Project Structure

```text
FindIt/
├── app.py
├── assets/
│   ├── logo.png
│   └── style.css
├── database/
│   └── db.py
├── ml/
│   └── matching.py
├── pages_backup/
├── requirements.txt
└── .gitignore
```

## 🚀 Run Locally

1. Clone the repository:

```bash
git clone https://github.com/ngeethika15/FindIt-Smart-Campus-Lost-and-Found.git
```

2. Navigate into the project:

```bash
cd FindIt-Smart-Campus-Lost-and-Found
```

3. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Start the application:

```bash
streamlit run app.py
```

## 🔮 Future Enhancements

- Image-based item recognition.
- More advanced natural language matching.
- Persistent cloud database integration.
- Email and notification support.
- Improved campus-wide deployment and scalability.

## 🎯 Project Objective

The goal of FindIt is to simplify the lost-and-found process within educational institutions by providing a centralized, accessible, and intelligent platform that helps students reconnect with their missing belongings.

---

**Developed as a course project.**