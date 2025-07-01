# notewriter

A Simple note taking app written in Python.

# Some Screenshots

![The home page of the editor.](/assets/home_page.png)
![What it looks like when actually editing the notes, in markdown.](/assets/editing_notes.png)
![The settings page.](/assets/settings.png)

# Completed
- General Features
  - [x] Markdown
  - [x] Relative Line Numbers
- Refactoring
  - [x] Refactor [note_area.py](https://github.com/zachakaquack/notewriter/blob/main/note_area.py) (the area where you actually write and view notes)

# Planned
- [ ] Refactoring
  - [ ] Refactor top bar to become more modular
  - [ ] Refactor bottom bar within notes to just make more sense and work better
  - [ ] Clean up code to use [file_management.py](https://github.com/zachakaquack/notewriter/blob/main/file_management.py) more instead of hardcoding
  - [ ] General optimizations
    - [ ] Make everything more type-safe
    - [ ] Optimize line number / relative line number drawing; currently it draws all numbers, not just the ones on the screen
- [ ] Search for notes by title
  - maybe within the file browser? I don't want to lose the home page's cards but I can't think of a way to incorporate the file browser.
  - left side file browser + tabs may just be the better way to go, i'll be real
- [ ] Searching within notes (ctrl-f)
- [ ] Release the program
  - [ ] Un-hardcode everything; conform to the plans for tombs [below](https://github.com/zachakaquack/notewriter/edit/main/README.md#plans-for-tombs).
  - if i get to releasing this once i get to this point, it'll most likely be released before tombs are implemented. so every note will still be in a place of your choosing, but the `config.json` will live within the folder and hold general config stuff, along with information for the notes.
- [ ] Different Tombs
  - File browser on left, instead of note home page?
- [ ] Templates
- [ ] Tags
- [ ] Sorting
### Dream Features
  - [ ] Vim Motions
    - [ ] learn regex...... lame!!!

## Plans for Tombs
Tombs are my copy of [obsidian](https://obsidian.md/)'s vaults. (thanks thesaurus.com). Each tomb will hold different files and folders.

Each tomb will have their own "settings", aka just the configuration for the files within the tomb. They'll be stored within `{TOMB_PATH}/.notewriter/config.json`. I don't know of any per-tomb settings as of writing this, so:

The main configuration file will be located at `~/.config/notewriter/config.json`. (on windows, `C:/Users/User/.config/notewriter/config.json`, or, if i feel like it, in appdata.)
