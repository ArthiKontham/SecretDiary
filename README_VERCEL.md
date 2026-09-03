# Secret Diary - Vercel Version

## Local run

```bash
pip install -r requirements.txt
python diary.py
```

Open http://127.0.0.1:5000

## Vercel

1. Push this folder to GitHub.
2. Import the repository into Vercel.
3. Vercel detects `vercel.json` and `api/index.py`.
4. Deploy.

Note: Vercel does not provide persistent writable storage for `users.txt`, `reminders.txt`, or `diaryEntries.txt`. For a real deployed app, replace these text files with a database such as Supabase/Postgres.

The Java Swing desktop window is kept for local use but is not launched by the web `/diary` route on Vercel. The web DiaryPage.html is used instead.


IMPORTANT VERCEL FIX
--------------------
Vercel's filesystem is read-only, so users.txt/reminders.txt/diaryEntries.txt cannot be used for persistent writes there.
Set these Production environment variables in Vercel:
- SUPABASE_URL = your Supabase project URL
- SUPABASE_SERVICE_ROLE_KEY = your Supabase service-role secret key
- FLASK_SECRET_KEY = a random secret string
Then redeploy. The app will use Supabase for users, diary entries, reminders, and calculations.
Do not paste the service-role key into HTML/JavaScript or commit it to GitHub.
