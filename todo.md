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
  - [ ] cloudfare bypass
  - [ ] allow custom folder structure
- [ ] manager
  - [ ] query selectors
    - [ ] chapters
      - [ ] single
      - [ ] ranges
    - [ ] volume
- [ ] storage
  - [x] async follow-up from download
  - [x] raw
    - [ ] allow for custom naming format
    - [ ] check number of images in each folder
- [ ] formatters
  - [ ] [cb*](https://en.wikipedia.org/wiki/Comic_book_archive)
  - [ ] pdf
    - [x] chapter
  - [x] serialize fetch
    - [x] python dict
    - [x] json
    - [x] yaml
    - [x] toml
- [ ] ui
  - [ ] cli
  - [ ] web
- [ ] providers
  - [x] routing



## Code quality

- [ ] error handling
  - [x] connection errors while downloading page


## Misc

- [ ] docs
- [ ] logo

