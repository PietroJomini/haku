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
  - [ ] better webpage fetch
- [ ] download
  - [x] async
    - [x] chunked, k sessions
    - [x] parallel, one session
    - [x] sequentials, one session
  - [x] limit rate
  - [x] allow retry on connection error 
  - [ ] cloudfare bypass
- [ ] manager
  - [ ] query ranges
- [ ] storage
  - [x] async follow-up from download
  - [x] raw
    - [ ] custom naming format
    - [ ] check number of images in each folder
    - [ ] json/yaml global meta
- [ ] formatters
  - [ ] [cb*](https://en.wikipedia.org/wiki/Comic_book_archive)
  - [ ] pdf
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

