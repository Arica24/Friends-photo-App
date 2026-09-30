"""Friends Photo App.

Coursework starter template: Girish Lukka.
Portfolio edition for Arica Bhuiyan, completed with AI assistance.
Original coursework specification was not supplied; see README for scope.
"""
import json
import copy
import uuid
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk, ImageOps

BASE = Path(__file__).resolve().parent
path = str(BASE / 'images')
MAX_PEOPLE = 5
NAVY = '#14263E'
BG = '#EFF4F9'
INK = '#20334B'
MUTED = '#60738B'
ACCENT = '#087F8C'
BORDER = '#D5E0EB'


def initial_people():
    # Illustrative connections only; these are not facts about the pictured people.
    names = ['Alex', 'Ali', 'Raj', 'Adam', 'Rima']
    links = {'Alex':['Ali','Rima'], 'Ali':['Alex','Raj'], 'Raj':['Ali','Adam'],
             'Adam':['Raj','Rima'], 'Rima':['Alex','Adam']}
    return [{'id':name.lower(), 'name':name, 'photo':f'images/{name.lower()}.png',
             'bio':'Add your own profile note.', 'friends':[n.lower() for n in links[name]]}
            for name in names]


class FriendStore:
    """Persist records separately from the interface; links are undirected."""
    def __init__(self, folder):
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=True)
        self.file = self.folder / 'friends.json'
        self.warning = None
        if self.file.exists():
            try:
                self.people = json.loads(self.file.read_text(encoding='utf-8'))
                self.validate()
            except (OSError, ValueError, TypeError, KeyError):
                self.people = initial_people()
                self.warning = 'The saved data could not be read. Demo profiles are shown; the old file has not been overwritten.'
        else:
            self.people = initial_people()

    def validate(self):
        if not isinstance(self.people, list) or len(self.people) > MAX_PEOPLE:
            raise ValueError('Invalid number of profiles')
        ids, names = set(), set()
        for person in self.people:
            if not isinstance(person, dict): raise ValueError('Invalid profile')
            for field in ['id','name','photo','bio']:
                if not isinstance(person.get(field), str): raise ValueError('Invalid field')
            if not person['id'] or person['id'] in ids or not person['name'].strip() or person['name'].casefold() in names:
                raise ValueError('Duplicate or empty profile')
            if not isinstance(person.get('friends'),list) or any(not isinstance(x,str) for x in person['friends']):
                raise ValueError('Invalid connections')
            ids.add(person['id']); names.add(person['name'].casefold())
        for person in self.people:
            if person['id'] in person['friends'] or any(x not in ids for x in person['friends']):
                raise ValueError('Invalid friend reference')
            if len(set(person['friends'])) != len(person['friends']): raise ValueError('Duplicate connection')
            for friend in person['friends']:
                if person['id'] not in self.get(friend)['friends']: raise ValueError('Non-mutual connection')

    def get(self, person_id):
        return next((p for p in self.people if p['id'] == person_id), None)

    def save(self):
        self.validate()
        temporary = self.file.with_suffix('.tmp')
        temporary.write_text(json.dumps(self.people, indent=2),encoding='utf-8')
        temporary.replace(self.file)

    def connect(self, first, second, connected):
        if first == second or not self.get(first) or not self.get(second):
            raise ValueError('Choose two different profiles')
        for a,b in [(first,second),(second,first)]:
            links=self.get(a)['friends']
            if connected and b not in links: links.append(b)
            elif not connected and b in links: links.remove(b)

    def remove(self, person_id):
        if not self.get(person_id): raise ValueError('Profile not found')
        self.people = [p for p in self.people if p['id'] != person_id]
        for p in self.people: p['friends'] = [x for x in p['friends'] if x != person_id]

    def suggestions(self, person_id):
        p = self.get(person_id)
        if p is None: return []
        found = set()
        for friend in p['friends']: found.update(self.get(friend)['friends'])
        return sorted(found - set(p['friends']) - {person_id})


class FriendsApp:
    def __init__(self, root, data_folder=None):
        self.root=root
        self.store=FriendStore(data_folder or Path.home()/'.friends-photo-app')
        self.selected=None
        self.photos=[]
        self.root.title('Friends Photo App | Arica Bhuiyan')
        self.root.geometry('1200x800')
        self.root.minsize(1000,700)
        self.root.configure(bg=BG)
        self.root.protocol('WM_DELETE_WINDOW',self.quitApp)
        style=ttk.Style(root)
        style.theme_use('clam')
        style.configure('TButton',font=('Arial',11),padding=(12,9),background='#E6EEF5',foreground=INK,borderwidth=0)
        style.map('TButton',background=[('active','#D6E5EF')],foreground=[('disabled','#8997A5')])
        style.configure('Accent.TButton',background=ACCENT,foreground='white')
        style.map('Accent.TButton',background=[('active','#056774')])
        style.configure('TEntry',padding=8,font=('Arial',12))
        style.configure('TCheckbutton',background='white',foreground=INK,font=('Arial',11))
        top=tk.Frame(root,bg=NAVY,height=80);top.pack(fill='x');top.pack_propagate(False)
        tk.Label(top,text='FRIENDS / PHOTO APP',bg=NAVY,fg='white',font=('Arial',18,'bold')).pack(side='left',padx=28)
        tk.Label(top,text='Five profiles. One little circle.',bg=NAVY,fg='#A8CADD',font=('Arial',11)).pack(side='right',padx=28)
        toolbar=tk.Frame(root,bg=BG);toolbar.pack(fill='x',padx=28,pady=(22,16))
        tk.Label(toolbar,text='Your circle',bg=BG,fg=INK,font=('Arial',24,'bold')).pack(side='left')
        self.add_button=ttk.Button(toolbar,text='+ Add person',style='Accent.TButton',command=self.addFriend);self.add_button.pack(side='right')
        ttk.Button(toolbar,text='Show all',command=self.showFriends).pack(side='right',padx=10)
        self.search=tk.StringVar()
        searchbar=tk.Frame(root,bg=BG);searchbar.pack(fill='x',padx=28,pady=(0,16))
        tk.Label(searchbar,text='Search name',bg=BG,fg=MUTED,font=('Arial',11)).pack(side='left',padx=(0,12))
        entry=ttk.Entry(searchbar,textvariable=self.search,width=25);entry.pack(side='left')
        self.count=tk.Label(searchbar,bg=BG,fg=MUTED,font=('Arial',11));self.count.pack(side='right')
        self.search.trace_add('write',lambda *_:self.render_cards())
        body=tk.Frame(root,bg=BG);body.pack(fill='both',expand=True,padx=28)
        self.cards=tk.Frame(body,bg=BG);self.cards.pack(side='left',fill='both',expand=True)
        detail_shell=tk.Frame(body,bg='white',width=330,highlightbackground=BORDER,highlightthickness=1)
        detail_shell.pack(side='right',fill='y',padx=(22,0));detail_shell.pack_propagate(False)
        detail_canvas=tk.Canvas(detail_shell,bg='white',highlightthickness=0,width=310)
        detail_scroll=ttk.Scrollbar(detail_shell,orient='vertical',command=detail_canvas.yview)
        detail_scroll.pack(side='right',fill='y');detail_canvas.pack(side='left',fill='both',expand=True)
        detail_canvas.configure(yscrollcommand=detail_scroll.set)
        self.detail=tk.Frame(detail_canvas,bg='white')
        detail_window=detail_canvas.create_window((0,0),window=self.detail,anchor='nw')
        self.detail.bind('<Configure>',lambda event:detail_canvas.configure(scrollregion=detail_canvas.bbox('all')))
        detail_canvas.bind('<Configure>',lambda event:detail_canvas.itemconfigure(detail_window,width=event.width))
        self.status=tk.StringVar(value='Select a person to view their profile. Connections are illustrative demo data.')
        foot=tk.Frame(root,bg=BG);foot.pack(fill='x',padx=28,pady=15)
        tk.Label(foot,textvariable=self.status,bg=BG,fg=MUTED,font=('Arial',10),anchor='w').pack(side='left',fill='x',expand=True)
        ttk.Button(foot,text='Clear selection',command=self.clearAll).pack(side='right',padx=8)
        ttk.Button(foot,text='Quit',command=self.quitApp).pack(side='right')
        self.render_cards();self.render_detail()
        if self.store.warning: self.root.after(100,lambda:messagebox.showwarning('Saved data',self.store.warning,parent=root))

    def image_path(self,person):
        p=Path(person['photo'])
        return p if p.is_absolute() else BASE/p

    def photo(self,person,size):
        try:
            with Image.open(self.image_path(person)) as source:
                im=ImageOps.fit(source.convert('RGB'),size,method=Image.Resampling.LANCZOS)
        except (OSError,ValueError):
            im=Image.new('RGB',size,'#C8DCE8')
        pic=ImageTk.PhotoImage(im,master=self.root);self.photos.append(pic);return pic

    def render_cards(self):
        for child in self.cards.winfo_children():child.destroy()
        self.photos=[]
        query=self.search.get().strip().casefold()
        people=[p for p in self.store.people if query in p['name'].casefold()]
        self.count.configure(text=f'{len(self.store.people)} / {MAX_PEOPLE} profiles')
        self.add_button.configure(state='normal' if len(self.store.people)<MAX_PEOPLE else 'disabled')
        for col in range(3):self.cards.columnconfigure(col,weight=1,uniform='cards')
        for row in range(2):self.cards.rowconfigure(row,weight=1)
        if not people:
            tk.Label(self.cards,text='No profiles match your search.' if self.store.people else 'Your circle is empty. Add a person to begin.',bg=BG,fg=MUTED,font=('Arial',13)).grid(row=0,column=0,columnspan=3,pady=45)
        for i,p in enumerate(people):
            selected=p['id']==self.selected
            card=tk.Frame(self.cards,bg='white',highlightbackground=ACCENT if selected else BORDER,highlightthickness=2 if selected else 1)
            card.grid(row=i//3,column=i%3,sticky='nsew',padx=(0,12),pady=(0,12))
            pic=self.photo(p,(132,132))
            image=tk.Label(card,image=pic,bg='white');image.pack(pady=(16,8))
            name=tk.Label(card,text=p['name'],bg='white',fg=INK,font=('Arial',15,'bold'));name.pack()
            tk.Label(card,text=f"{len(p['friends'])} connections",bg='white',fg=MUTED,font=('Arial',10)).pack(pady=(2,8))
            ttk.Button(card,text='View profile',command=lambda person=p['id']:self.friendButton(person)).pack(pady=(0,14),padx=10)
            for widget in [card,image,name]:widget.bind('<Button-1>',lambda event,person=p['id']:self.friendButton(person))
        # Recreate detail image too, after old references have been released.
        self.render_detail()

    def render_detail(self):
        for child in self.detail.winfo_children():child.destroy()
        person=self.store.get(self.selected)
        if person is None:
            tk.Label(self.detail,text='A closer look',bg='white',fg=INK,font=('Arial',19,'bold')).pack(pady=(40,12))
            tk.Label(self.detail,text='Choose one of the five profiles\nto see details and connections.',bg='white',fg=MUTED,font=('Arial',12),justify='center').pack(padx=20,pady=15)
            return
        pic=self.photo(person,(110,110))
        tk.Label(self.detail,image=pic,bg='white').pack(pady=(22,10))
        tk.Label(self.detail,text=person['name'],bg='white',fg=INK,font=('Arial',21,'bold'),wraplength=280).pack()
        tk.Label(self.detail,text=person['bio'],bg='white',fg=MUTED,font=('Arial',11),wraplength=275,justify='center').pack(padx=20,pady=(8,18))
        tk.Label(self.detail,text='FRIENDS',bg='white',fg=ACCENT,font=('Arial',10,'bold')).pack(anchor='w',padx=22)
        for identity in person['friends']:
            friend=self.store.get(identity)
            ttk.Button(self.detail,text=friend['name'],command=lambda x=identity:self.friendButton(x)).pack(fill='x',padx=22,pady=3)
        if not person['friends']:tk.Label(self.detail,text='No connections yet.',bg='white',fg=MUTED,font=('Arial',11)).pack(anchor='w',padx=22,pady=5)
        suggested=self.store.suggestions(person['id'])
        label=', '.join(self.store.get(x)['name'] for x in suggested) or 'None yet'
        tk.Label(self.detail,text='FRIENDS OF FRIENDS',bg='white',fg=ACCENT,font=('Arial',10,'bold')).pack(anchor='w',padx=22,pady=(16,3))
        tk.Label(self.detail,text=label,bg='white',fg=MUTED,font=('Arial',11),wraplength=275,justify='left').pack(anchor='w',padx=22,pady=(0,14))
        ttk.Button(self.detail,text='Edit profile & connections',command=lambda:self.edit_profile(person)).pack(fill='x',padx=22,pady=4)
        ttk.Button(self.detail,text='Delete person',command=self.delFriend).pack(fill='x',padx=22,pady=4)

    def friendButton(self,identity):
        self.selected=identity;self.render_cards()
        self.status.set(f"Viewing {self.store.get(identity)['name']}. Edit their details or connections from the profile panel.")

    def showFriends(self):
        self.search.set('');self.render_cards();self.status.set('Showing all saved profiles.')

    def clearAll(self):
        self.selected=None;self.search.set('');self.render_cards();self.status.set('Selection cleared. Your saved profiles have not been deleted.')

    def commit(self):
        try:self.store.save();return True
        except (OSError,ValueError) as error:
            messagebox.showerror('Could not save',f'Your changes could not be written to disk.\n{error}',parent=self.root)
            self.status.set('Save failed. Changes are currently only in memory.');return False

    def delFriend(self):
        person=self.store.get(self.selected)
        if person and messagebox.askyesno('Delete person',f"Remove {person['name']} and their connections?",parent=self.root):
            previous=copy.deepcopy(self.store.people)
            self.store.remove(person['id']);self.selected=None
            saved=self.commit()
            if not saved:self.store.people=previous
            self.render_cards()
            if saved:self.status.set('Profile deleted. You can add a replacement; the limit remains five.')

    def addFriend(self):
        if len(self.store.people)>=MAX_PEOPLE:
            messagebox.showinfo('Five-person limit','Delete a profile before adding a replacement.',parent=self.root);return
        self.edit_profile(None)

    def edit_profile(self,person):
        dialog=tk.Toplevel(self.root);dialog.title('Edit person' if person else 'Add person');dialog.configure(bg='white')
        dialog.geometry('440x640');dialog.resizable(False,False);dialog.transient(self.root);dialog.grab_set()
        form=tk.Frame(dialog,bg='white');form.pack(fill='both',expand=True,padx=25,pady=20)
        tk.Label(form,text='Edit profile' if person else 'New profile',font=('Arial',21,'bold'),bg='white',fg=INK).pack(anchor='w',pady=(0,15))
        def label(text):tk.Label(form,text=text,bg='white',fg=INK,font=('Arial',11,'bold')).pack(anchor='w',pady=(10,5))
        label('Name')
        name=tk.StringVar(value=person['name'] if person else '')
        entry=ttk.Entry(form,textvariable=name);entry.pack(fill='x');entry.focus_set()
        label('Profile note (up to 160 characters)')
        bio=tk.Text(form,height=3,font=('Arial',11),wrap='word',relief='solid',borderwidth=1);bio.pack(fill='x')
        bio.insert('1.0',person['bio'] if person else '')
        chosen={'file':None}
        photo_label=tk.StringVar(value='Keep current photo' if person else 'No photo chosen')
        def choose():
            filename=filedialog.askopenfilename(parent=dialog,title='Choose a profile photo',filetypes=[('Image files','*.png *.jpg *.jpeg *.webp'),('All files','*')])
            if filename:
                try:
                    with Image.open(filename) as source:source.verify()
                except (OSError,ValueError):messagebox.showerror('Photo','Choose a readable image.',parent=dialog);return
                chosen['file']=filename;photo_label.set(Path(filename).name)
        label('Photo')
        ttk.Button(form,text='Choose photo',command=choose).pack(anchor='w')
        tk.Label(form,textvariable=photo_label,bg='white',fg=MUTED,font=('Arial',10),wraplength=370).pack(anchor='w',pady=5)
        label('Connections (mutual)')
        checks={}
        for other in self.store.people:
            if person and other['id']==person['id']:continue
            var=tk.BooleanVar(value=bool(person and other['id'] in person['friends']));checks[other['id']]=var
            ttk.Checkbutton(form,text=other['name'],variable=var).pack(anchor='w',pady=2)
        if not checks:tk.Label(form,text='Add another person to create connections.',bg='white',fg=MUTED).pack(anchor='w')
        def save():
            entered=name.get().strip();note=bio.get('1.0','end-1c').strip()
            if not 1<=len(entered)<=24 or any(ord(c)<32 for c in entered):
                messagebox.showerror('Name','Enter a name of 1–24 printable characters.',parent=dialog);return
            if any(p['name'].casefold()==entered.casefold() and (not person or p['id']!=person['id']) for p in self.store.people):
                messagebox.showerror('Name','A profile already uses that name.',parent=dialog);return
            if len(note)>160:messagebox.showerror('Profile note','Keep the note to 160 characters.',parent=dialog);return
            if person is None and len(self.store.people)>=MAX_PEOPLE:return
            identity=person['id'] if person else uuid.uuid4().hex
            photo=person['photo'] if person else ''
            if chosen['file']:
                dest=self.store.folder/'photos';dest.mkdir(exist_ok=True)
                target=dest/(uuid.uuid4().hex+'.png')
                try:
                    with Image.open(chosen['file']) as source:
                        ImageOps.fit(source.convert('RGB'),(400,400),method=Image.Resampling.LANCZOS).save(target)
                except (OSError,ValueError) as error:
                    messagebox.showerror('Photo',f'Could not save the selected image.\n{error}',parent=dialog);return
                photo=str(target)
            previous=copy.deepcopy(self.store.people)
            if person is None:
                person_record={'id':identity,'name':entered,'bio':note,'photo':photo,'friends':[]};self.store.people.append(person_record)
            else:person.update(name=entered,bio=note,photo=photo)
            for other,var in checks.items():self.store.connect(identity,other,var.get())
            saved=self.commit()
            if not saved:
                self.store.people=previous
                dialog.destroy()
                self.render_cards()
                self.status.set('Save failed. Your previous profiles are unchanged.')
                return
            self.selected=identity;self.render_cards()
            self.status.set('Profile saved. Changes will be here next time you open the app.');dialog.destroy()
        controls=tk.Frame(form,bg='white');controls.pack(side='bottom',fill='x',pady=(18,0))
        ttk.Button(controls,text='Cancel',command=dialog.destroy).pack(side='left')
        ttk.Button(controls,text='Save profile',style='Accent.TButton',command=save).pack(side='right')

    def quitApp(self):
        self.root.destroy()


# Starter function names retained as wrappers for the completed interface.
def showFriends():myApp.showFriends()
def friendButton(identity):myApp.friendButton(identity)
def clearAll():myApp.clearAll()
def delFriend():myApp.delFriend()
def addFriend():myApp.addFriend()
def quitApp():myApp.quitApp()

if __name__ == '__main__':
    window=tk.Tk()
    myApp=FriendsApp(window)
    window.mainloop()
