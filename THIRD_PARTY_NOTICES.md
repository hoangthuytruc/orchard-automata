# Third-party notices

## code-review-skill

Source: https://github.com/awesome-skills/code-review-skill

Version taken: the source states no version number or release tag, and the copy read carried no commit id. The copy
was read in November 2026. If the exact upstream commit matters, compare against the repository history of that
month.

Used in: `references/review-checklist.md`. What was taken, paraphrased and merged into the checklist's existing
sections (no file was copied whole): the review process (context first, high-level review, line review, summary), the
Swift and SwiftUI review guide, the architecture review guide, the universal code-quality guide, and the Swift parts
of the common-bugs checklist, the concurrency and error-handling guides, the security review guide and the
performance review guide. Guidance for other languages and platforms was not taken. Its severity labels and review
template were not taken; the checklist keeps its own.

Licence:

```
MIT License

Copyright (c) 2025 awesome-skills

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Vocabulary for testing

`references/test-strategy.md` describes tests on four axes following Alperen Keles's vocabulary for testing
(https://alperenkeles.com/posts/vocab-for-testing/). The axes are named and cited; no text was copied.

## concord-skill-lean-testing

Source: https://github.com/bqp007/concord-skill-lean-testing

Version taken: the source states no version number or release tag. The copy was read on November 27, 2026; the
repository's last push was dated November 20, 2026.

Used in: `references/test-strategy.md`, sections 16 and 17, and the lines of `references/review-checklist.md`,
section 10, that point to them. What was taken, paraphrased and fitted to the scenario model (no file was copied
whole): the rule that an expected value must come from a source that outranks the code; that a tuned configuration
value is not behaviour; the description of a finished test set (complete, minimal, consistent with the suite); how
a new case is weighed against the existing tests and what a red existing test means; and the evidence a finding on
a test must show. Not taken: its rule against test doubles for the project's own modules (the strategy keeps fakes
behind protocols at layer boundaries), its guidance on guards at trust boundaries, and its position that no
procedure is prescribed.

Licence:

```
MIT License

Copyright (c) 2026 Bao Q. Pham

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
