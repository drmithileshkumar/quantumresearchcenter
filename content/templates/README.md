# Adding a student and their research contributions

Copy the object in [student.json](student.json) into the `students` array in
[../student.json](../student.json). Replace the placeholder text and remove
unused optional fields and output links. The template is not published by itself.
Do not edit the generated `research/students/index.html` directly.

Each student appears once. Add one object to their `contributions` array for each
problem they worked on. For a shared project, list each student's specific role
under their own entry; the project and output links may be shared.

| Field | What to enter |
| --- | --- |
| `name` | Student's display name. Required. |
| `affiliation` | Department or institution. Optional. |
| `contributions` | One or more problems or projects. |
| `title` | A short problem or project title. Required. |
| `topic` | Link to the relevant research topic or detailed project page, relative to the repository root. Optional. |
| `problem` | The research question and scope. Optional. |
| `description` | What this student did and what resulted. Required. |
| `period` | Actual dates or academic years of participation. Optional. |
| `status` | Project status, such as Ongoing, Completed, or Paused. Optional. |
| `outputs` | Any number of available outputs, each with a descriptive `label` and a `url`. Optional; use `[]` or omit it when there are none. |

GitHub, preprint, and accepted-paper links are independent: include whichever
exist. Use the actual paper title and venue in paper labels. A preprint can remain
linked alongside the accepted paper. If an accepted paper has no publisher link
yet, link its available manuscript and identify the acceptance venue in the label.
Use “Published paper” when appropriate. Keep publication status in the output
label, separate from the project's overall status.

All example URLs in the template are placeholders. Replace or remove them before
adding the entry. Local report and presentation paths are relative to the repository
root; external links use full HTTPS URLs.

From the repository root, run:

```sh
python3 scripts/build.py
python3 scripts/build.py --check
```

The build regenerates the Students and Contributions page and checks local links.
