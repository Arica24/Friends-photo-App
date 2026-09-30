# Friends Photo App

A Python desktop application built from a Tkinter coursework starter. It opens with **five people only: Alex, Ali, Raj, Adam and Rima**.

## Features

- Five photo cards with search by name.
- Select a person to see their photo, profile note and connections.
- Edit a name, profile note or photo.
- Set mutual friend connections with checkboxes.
- See friends-of-friends, excluding the person and their direct friends.
- Delete a profile with confirmation.
- Add a replacement when fewer than five profiles remain. A sixth person is blocked.
- Clear the selection without deleting saved profiles.
- Save changes automatically for the next session.

The initial connections are illustrative demo data, not facts about the people in the photographs.

## Run on a Mac

Install Python 3.9 or newer with Tkinter support. Keep all files and the `images` folder together.

Open Terminal in the extracted `friends-photo-app` folder, then run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 myAppStarter.py
```

A desktop window opens. This is not a browser app, and it does not need Flask.

To check Tkinter is available:

```bash
python3 -m tkinter
```

If this fails, install a Python distribution with Tk support. Tkinter is not installed through `pip install tkinter`.

## Windows

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python myAppStarter.py
```

## Using the app

1. Select **View profile** below a photograph.
2. Choose **Edit profile & connections**.
3. Update the details or choose another image.
4. Tick or untick connections, then choose **Save profile**.
5. Choose a friend's name in the side panel to switch profiles.
6. Use **Clear selection** to return to the starting view.

**Add person** is disabled when five profiles exist. Delete a person first if you want to add a replacement. Deletion removes their connections too. It does not remove the original supplied images.

## Storage

Changes are saved locally under `.friends-photo-app` in your home folder. The app copies newly chosen photos into its local data folder so it does not depend on the original file remaining in place. Initial supplied images are read from the project's `images` folder.

If you move the project to another computer, your edits do not follow automatically. The download contains only the five initial profiles. Local data is not encrypted.

## Testing

```bash
python3 -m unittest -v
```

Seven data tests cover the five starting profiles, persistence, mutual connections, deleted-profile cleanup, friends-of-friends, rejecting a sixth profile and handling an unreadable saved file.

## Project files

- `myAppStarter.py`: completed interface and data model, retaining the starter function names.
- `images/`: the five supplied profile pictures.
- `requirements.txt`: Pillow dependency.
- `test_friends.py`: data behaviour tests.
- `.gitignore`: excludes virtual environments and Python caches.


