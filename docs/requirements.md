# SignalQ requirements

**Setting:** Telecom service center, Monday to Saturday walk-in consultations (SIM registration, SIM replacement, line activation, postpaid and fiber applications, bill payment, technical support).
**People who wait:** Customers who walk in for telecom services, such as Joanna Sanchez, a sari-sari store owner looking for a SIM Replacement.
**People who serve:** Customer service staff at the counters, such as Michael Blackwood, a Senior Customer Service Representative.

**Problem statement:** A customer who visits the service center needs a way to see how many people are ahead of her and step out without losing her turn, because the "Now Serving" display shows only the numbers being served and she cannot tell how many people are ahead of her. The staff member who serves her needs to know what service she came for before she reaches the counter, because he otherwise calls a bare number and can lose about 10 minutes before realizing the issue belongs elsewhere.

## Functional Requirements

| ID | Requirement | Priority | Stores Data? | Status |
| --- | --- | --- | --- | --- |
| FR-01 | A customer can join the queue by entering their name, phone number, email (optional), and service required. | Must | Yes | Built (Week 3) |
| FR-02 ★ | A customer can see their ticket number, service, status, position, assigned counter, and how long they have been waiting. | Must | Yes | Built (Week 3);  waiting duration pending |
| FR-03 | A customer can voluntarily leave the queue. | Must | Yes | Built (Week 3) |
| FR-04 | A staff member can view all active waiting and called tickets with number, service type, and status in the order they joined. | Must | Yes | Built (Week 3) |
| FR-05 | A staff member can call a waiting ticket to their counter. | Must | Yes | Built (Week 3) |
| FR-06 | A staff member can mark a ticket as served or a no-show. _(Split from FR-05)_ | Must | Yes | Built (Week 3) |
| FR-07 | A staff member can add, rename, and deactivate a service. Deactivated services cannot accept new tickets, but existing tickets can still be served. | Must | Yes | This week |
| FR-08 ★ | A customer can choose an account type (prepaid, postpaid or business) when joining the queue. | Should | Yes | Later |
| FR-09 ★ | A staff member can see each ticket’s account type next to its service on the dashboard. | Should | Yes | Later |
| FR-10 ★ | A customer can request priority when joining the queue by choosing a reason (senior citizen, PWD or pregnant). | Could | Yes | Later |
| FR-11 | A staff member can see which waiting tickets are priority. | Could | Yes | Later |


## Non-functional Requirements

| ID | Requirement | Category | Priority |
| --- | --- | --- | --- | 
| NFR-01 | No ticket is lost when the server or the database restarts. | Reliability | Must |
| NFR-02 | Two people can never get the same ticket number, even if they join at the same moment. | Data integrity | Must |
| NFR-03 | Deactivating a service never deletes its existing tickets or moves them to another service. | Data integrity | Must |
| NFR-04 | A ticket keeps its record after it is served, marked no-show or left, so staff can report on past tickets. | Data integrity | Should |
| NFR-05 | My place loads in under 2 seconds under simulated 4G network conditions. | Performance | Should |
| NFR-06 | Every screen scores 90 or higher in the Lighthouse accessibility check. | Accessibility | Must |
| NFR-07 | My place refreshes the ticket status by itself at least every 10 seconds, without a page reload. | Reliability | Must |
| NFR-08 | No password or secret key is stored in the repository. | Security | Must |
| NFR-09 | A customer can only view or leave their own ticket. A request for another customer's ticket is refused. | Privacy | Should |

## MVP

**MVP:** FR-01 to FR-07 and the **Must** NFRs (_NFR-01 to NFR-03_ and _NFR-06 to NFR-08_).

This is the smallest version that still solves the problem: a customer can join with the service they need, see how many people are ahead and step out without losing their turn, and staff can see the service on each ticket, call it, and record the outcome. The remaining *Should* and *Could* rows improve the queue but do not change whether a customer can wait remotely.

## Out of scope

| Feature | Why it is not built this semester |
| --- | --- |
| SMS or phone-call notification when a ticket is called | Sending texts or calls needs either a paid SMS service or a real SIM and load, and this is a student project with little to zero budget. My place refreshes by itself and shows the status and counter instead. |
| Customer document uploads | Uploads need secure file storage, access controls, and a way for staff to review and verify each file, which is far more than a queue needs. Customers show their documents at the counter instead, and staff already see the service they came for before calling them. |

## Feedback
| Who (role only, no full name) | What they said | What I changed |
| --- | --- | --- |
| Customer | "Can I also see how long I've been waiting? It would help me keep track of the time I've spent in the queue." | Revised FR-02 to display how long the customer has been waiting on the My place page. | 