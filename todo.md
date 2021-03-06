# TODOS

## Features

- [x] fetch
  - [ ] parse title with separate function
    - [ ] somehow the user should be able to modify it
  - [x] chapters
    - [x] url
    - [x] title
    - [x] index
    - [x] volume
    - [ ] numerical index
  - [x] pages
    - [x] url
    - [x] index
  - [x] title
  - [ ] generic meta, not mandatory
    - [x] cover
    - [ ] artist(s)
    - [ ] ongoing / completed
  - [x] better helpers scrape
    - [x] cached
    - [x] more flexible
- [ ] download
  - [x] async
    - [x] chunked, k sessions
    - [x] parallel, one session
    - [x] sequentials, one session
  - [x] limit rate
  - [x] allow retry on connection error 
  - [ ] resume, comparing dir tree with serialized yaml (json?)
  - [ ] cloudfare bypass
    - [ ] investigate!
    - [x] simple (referer) (!?)
  - [x] allow custom folder structure (customizing an FTree)
- [ ] shelf
  - [ ] filters
    - [x] chapter
      - [x] index
      - [x] title
    - [ ] volume
- [ ] storage
  - [x] async follow-up from download
  - [x] raw
    - [x] formalize folders tree creation
    - [x] allow for custom naming format
    - [ ] save images on different thread process
    - [ ] check number of images in each folder
- [ ] formatters
  - [ ] [cb*](https://en.wikipedia.org/wiki/Comic_book_archive)
  - [ ] pdf
    - [ ] multiprocessing?
    - [x] chapter
    - [ ] merge
      - [ ] chunk size modifier
      - [ ] bookmarks
      - [x] rawly merge
  - [ ] epub
  - [x] serialize fetch
    - [x] python dict
    - [x] json
    - [x] yaml
    - [x] toml
- [ ] ui
  - [ ] cli
    - [ ] features
      - [ ] fetch
        - [ ] display full info
          - [ ] meta
          - [ ] chapters
            - [ ] index
            - [ ] title
            - [ ] url
            - [ ] volume
      - [ ] download
        - [ ] if convert, to temp dir
      - [ ] convert
      - [ ] filter
    - [ ] args
      - [x] url REQUIRED
      - [x] path
      - [x] output format
      - [x] download batch size
      - [ ] filters
      - [x] only fetch
  - [ ] web
- [ ] providers
  - [x] routing



## Code quality

- [x] linting
  - [x] black
  - [x] isort
  - [x] flake8
- [ ] error handling
  - [x] connection errors while downloading page


## Misc

- [ ] docs
- [ ] logo

