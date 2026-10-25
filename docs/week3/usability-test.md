# Usability test

## Participant

**TJ** tested the app on a Desktop PC on October 25, 2026. TJ acted as both personas, the person waiting (**Joanna Sanchez**) and the staff member (**Michael Blackwood**), but is closer to Michael: he has extensive experience with digital systems. 

## Results

| Task | Persona | Finished? | Time | Hesitations, comments, surprises |
| --- | --- | --- | --- | --- |
| 1. "You just arrived. Get in line for SIM Registration." | Joanna | Yes | about 7-10s | TJ found the **Join the queue** button on the home page right away and moved through the form easily. He filled in each field and picked a service without hesitating, and he did not need any help. |
| 2. "How many people are ahead of you? What is your number?" | Joanna | Yes | about 3s | After joining, TJ went straight to the large ticket number and the "people ahead of you" sentence on My place. He answered both questions correctly and quickly, and the status badge needed no explanation. |
| 3. "Pretend you are the staff member. Call the next person and mark them as served." | Michael | Yes | about 5s | TJ opened the Staff page from the navbar without help and found **Call Next** at the top of the dashboard. He called the ticket and marked it served on his own, with no wrong clicks. |

## Which design rules held up

### Michael (staff member)

| Rule | Held up? | Evidence |
| --- | --- | --- |
| 1. Show each ticket's service next to its number | Yes | TJ saw the service on the dashboard without help. |
| 2. Show a Call button at the top, ready as soon as he finishes | Yes | TJ found **Call Next** at the top of the dashboard right away. |
| 3. Mark Served or No-show on the called ticket, with a quick confirmation | Partly | Served and No-show are on the called ticket and TJ used them without trouble. **There is no confirmation step**, so this part is partly met. |
| 4. Large, high-contrast buttons, no hidden menus | Yes | Nothing was hidden in the menu. |

### Joanna (person waiting)

| Rule | Held up? | Evidence |
| --- | --- | --- |
| 1. Show position as a plain sentence | Yes | TJ read "3 people ahead of you" and answered Task 2 correctly. |
| 2. Update on its own, show status and counter large, show "last updated" | Yes | TJ saw that his ticket updated every 10 seconds with the Last Updated timestamp. |
| 3. Make "Leave queue" easy to find, with a confirmation screen | Partly | The button is easy to find, but **there is no confirmation** screen. |
| 4. Large buttons and text, light page | Yes | TJ saw that the UI was readable on mobile devices. |
| 5. Choose a specific service on joining, show it on the ticket and staff row | Yes | TJ chose a service on Join, and it appeared on My place and on the staff dashboard. |

## One improvement

**Problem:** Marking No-show and Leave queue are permanent single clicks. Michael's rule 3 and Joanna's rule 3 both call for a confirmation, and a mis-tap cannot be easily undone. 

**Fix:** Add confirmation for leave and no-show. Accidental misclick will cause a slip that is difficult to undo.

**Before:**

![Before](screenshots/before.png) 

**After:**

![After](screenshots/after.png)