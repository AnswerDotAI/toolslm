# Release notes

<!-- do not remove -->

## 0.2.3

### New Features

- Handle list and dict args to `mk_ns` ([#34](https://github.com/AnswerDotAI/toolslm/issues/34))


## 0.2.2

### New Features

- Auto clean up bad param names in `call_func` ([#33](https://github.com/AnswerDotAI/toolslm/issues/33))

### Bugs Squashed

- python() function can't be used as a tool ([#32](https://github.com/AnswerDotAI/toolslm/issues/32))


## 0.2.1

### New Features

- Optionally dont raise error on `call_func` ([#31](https://github.com/AnswerDotAI/toolslm/pull/31)), thanks to [@erikgaas](https://github.com/erikgaas)
- dict support in `get_schema` ([#30](https://github.com/AnswerDotAI/toolslm/issues/30))


## 0.2.0

### Breaking changes

- Optional libs (http2text, beautifulsoup, llms_txt) are no longer automatically installed

### New Features

- Lazily load optional modules ([#29](https://github.com/AnswerDotAI/toolslm/issues/29))


## 0.1.3

### New Features

- Pass glb,loc to python ([#28](https://github.com/AnswerDotAI/toolslm/issues/28))

## 0.1.2

### New Features

- Adds `call_func_async` ([#27](https://github.com/AnswerDotAI/toolslm/pull/27)), thanks to [@mikonapoli](https://github.com/mikonapoli)
- Add arg ignore links ([#26](https://github.com/AnswerDotAI/toolslm/pull/26)), thanks to [@Isaac-Flath](https://github.com/Isaac-Flath)


## 0.1.1

### New Features

- Add arg ignore links ([#26](https://github.com/AnswerDotAI/toolslm/pull/26)), thanks to [@Isaac-Flath](https://github.com/Isaac-Flath)

### Bugs Squashed

- fix: prevent markdown heading detection inside code blocks ([#25](https://github.com/AnswerDotAI/toolslm/pull/25)), thanks to [@franckalbinet](https://github.com/franckalbinet)
- Fix markdown hierarchy parsing for arbitrary header levels ([#22](https://github.com/AnswerDotAI/toolslm/pull/22)), thanks to [@erikgaas](https://github.com/erikgaas)


## 0.1.0

### Breaking changes

- Replace `source` with `src` in context generation ([#17](https://github.com/AnswerDotAI/toolslm/issues/17))


## 0.0.8

### New Features

- Escape and print context in `folder2ctx` et al ([#16](https://github.com/AnswerDotAI/toolslm/issues/16))


## 0.0.7

### New Features

- Add `dict2obj` to `md_hier` funcs ([#15](https://github.com/AnswerDotAI/toolslm/issues/15))
- Migrate call_func from claudette to toolslm ([#14](https://github.com/AnswerDotAI/toolslm/pull/14)), thanks to [@ncoop57](https://github.com/ncoop57)
- Allow for getting schemas from nested structures ([#11](https://github.com/AnswerDotAI/toolslm/pull/11)), thanks to [@ncoop57](https://github.com/ncoop57)
- Allow for `sel` to select and wrap multiple element results ([#10](https://github.com/AnswerDotAI/toolslm/pull/10)), thanks to [@Isaac-Flath](https://github.com/Isaac-Flath)

### Bugs Squashed

- Using `get_schema` on class method results in type missing error ([#12](https://github.com/AnswerDotAI/toolslm/issues/12))


## 0.0.6

### New Features

- Add `read_docs` and `find_docs` ([#8](https://github.com/AnswerDotAI/toolslm/issues/8))


## 0.0.5

### Bugs Squashed

- XML tools assume all files have content ([#3](https://github.com/AnswerDotAI/toolslm/issues/3))


## 0.0.4

- Minor updates

## 0.0.2

- Rename project


## 0.0.1

- Initial alpha release

