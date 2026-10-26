## Michael Blackwood, the staff member

> "I feel like it would be easier if I could see ticket details. Like seeing 'Ticket 304' is here for SIM registration or a bill payment would be a helpful detail. It gives me immediate context on what to prepare for."

| | |
| --- | --- |
| **Photo or sketch** | ![Persona 1 Michael Blackwood](screenshots/pexels-pavel-danilyuk-7658358.jpg) |
| **Age, role and background** | 34, Senior Customer Service Representative. Has 6 years in handling walk-in consultations at a service center, specifically Counter 2. |
| **Goals** | 1. Keep his counter busy with no unnecessary idle gaps in between, even when someone doesn't show up. (observation) <br> 2. Know what service each customer needs before they reach his counter, so he can prepare the right tools. <br> 3. Record each ticket’s outcome quickly and accurately, so the queue stays up to date and moves on.|
| **Frustrations** | 1. Calling the next ticket number without knowing the service needed, so he can’t prepare the needed things in advance. <br> 2. He spends about 10 minutes with a customer before realizing the issue (e.g., a corporate account change) can’t be resolved at his counter and has to redirect them. (observation) <br> 3. Finishes one customer and has to wait for who is next, and when a called customer doesn’t come to the counter, his counter sits idle until he decides to move on, wasting valuable time. (observation)| 
| **Devices and context** | Desktop PC at Counter 2 in the service center, used for customer accounts and documents. He calls customers through a "Now Serving" display, so all he has for the next customer is a number, with no service or details attached. | 
| **Tech comfort** | High. He has used the service center's current systems for 6 years, so he expects fast and efficient tools. |
| **Accessibility needs** | Uses the desktop all day while switching between customer documents and the screen, so he needs high-contrast text, buttons that are easily discernible and are easy to hit with a mouse. Works at a shared counter, so no hidden menus slowing him down between customers. |

### Scenario

After Michael finishes assisting a customer with their query regarding bill payments on counter 2, he checks out his staff dashboard, marks the ticket as served and finds that the next ticket to be attended is ticket 304 and is for SIM registration. He prepares the registration form and list of documents required by the customer before calling the customer. The customer arrives at his counter and he begins immediately. In another case, ticket 307 is called but no one appears so he marks it as no show and moves on to the next ticket.

### Top tasks in the app

| Task | Screen | Requirement ID |
| --- | --- | --- |
| See each waiting ticket's number, service and status | Staff dashboard | FR-04 |
| Call the next ticket to his counter | Staff dashboard | FR-05 |
| Mark a ticket as served | Staff dashboard | FR-05 |
| Mark a ticket as a no-show | Staff dashboard | FR-05 |

### What this means for my interface

1. Because he calls customers knowing only a ticket number, and can spend about 10 minutes before realizing the issue isn't his to handle, my interface must show each ticket's service next to its number. (observation) 
2. Because his counter can sit idle between customers, my interface must show the next waiting ticket with a Call button at the top of the dashboard, ready to be handled as soon as he finishes.
3. Because he needs to record outcomes quickly but accurately, and a customer sometimes doesn't arrive, my interface must let him mark Served or No-show on the called ticket itself, with a quick confirmation before it's final. 
4. Because he switches between handling documents and using the Desktop PC, my interface must use large, high-contrast buttons with clear text labels, with no hidden menus. (observation)


## Joanna Sanchez, the person waiting

> "Whenever I go to a service center to get help for my retailer SIM, I have to go through a lengthy process, and I'm not even sure how many people are ahead of me, or if I can step out for a moment."

| | |
| --- | --- |
| **Photo or sketch** | ![Persona 2 Joanna Sanchez](screenshots/pexels-mikegles-16866941.jpg)|
| **Age, role and background** | 44, owner of a small neighborhood sari-sari store that earns most of its money from selling prepaid load. Her retailer SIM stopped working, so she can't sell load. Her 15-year-old daughter Lia watches the store until she has to leave for school |
| **Goals** | 1. Get her retailer SIM replaced so she can sell prepaid load again, since prepaid load is most of her income.<br>2. Step out to check on the store and Lia, and come back without losing her turn. <br>3. Get her problem treated as what it is, by telling staff exactly what service she needs when she joins the queue.|
| **Frustrations** | 1. Once she arrives at the service center, she can't tell how long the line will take, and every hour away means a closed store and lost revenue. (observation) <br> 2. She has a printed ticket number, but the only way to know her turn is watching the "Now Serving" display, so she can't risk stepping out to do something else important without missing it. (observation) <br> 3. The display only shows the number being served, so she can't tell how many people are ahead of her and ends up guessing by counting heads in the lobby.
| **Tech comfort** | Medium. She already uses her phone to sell load, but she is not patient with apps that need sign-up or many taps. |
| **Accessibility needs** | One hand is often busy holding her bag, so large tap targets are needed. Status must be shown in words, not by color alone. Limited mobile data means pages must load fast and use little data. |


### Scenario

The time is 10:20 am on Wednesday, and Joanna has two hours before Lia has to go to school. She enters the service center to see that the lobby is very crowded and opens the website on her cell phone while carrying her bag. She selects "Bill inquiry" and enters her name, email, and cell phone number to get ticket number 318. She sees from the webpage that there are five people ahead of her and the time when it was last updated, but she still notes down the ticket number on the receipt. She looks for a comfortable spot and waits for her turn. Once called, the ticket status is updated and she is alerted and directed to which counter is serving her.

### Top tasks in the app

| Task | Screen | Requirement ID |
| --- | --- | --- |
| Pick the right service and join the queue | Join | FR-01 |
| Check ticket number, service, status and position | My place | FR-02 |
| See the assigned counter once called | My place | FR-02 |
| Leave the queue if the store needs her | My place | FR-03 |

### What this means for my interface

1. Because the "Now Serving" screen only shows the current number, the My place screen must show her position as a plain sentence, "5 people ahead of you".
2. Because staying alert all the time for her number is tiring and she may need to step out to check the store, my interface must update the My place screen on its own, show the ticket status and her counter in large text, and show a "last updated" time. It must keep showing the last known status if the connection drops.
3. Because the store needs her and she may have to give up her place, my interface must make "Leave queue" easy to find with a confirmation screen.
4. Because she holds her bag in one hand and has limited mobile data, my interface must use large buttons and text and load a light page.
5. Because staff should know what she needs, my interface must have her choose a specific service when she joins the queue and show it on her ticket and on her row in the staff dashboard.