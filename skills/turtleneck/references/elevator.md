# The elevator lens

Drawn from Gregor Hohpe's work: The Software Architect Elevator, 37 Things
One Architect Knows About IT Transformation, Cloud Strategy, Platform
Strategy, and Enterprise Integration Patterns. This file holds the working
questions, not the books. Read the books.

## Two floors

An architect rides between the penthouse, where business decisions are
made, and the engine room, where the system runs. Value comes from
connecting the floors, not from living on one. A decision described on only
one floor is not a decision yet.

Penthouse questions:

- What changes for the business if this goes well? In money, time, risk, or
  options, not in components.
- Who pays for building it? Who pays for running it in year three?
- What does the business lose if we do nothing for a year?
- Which future does this close off, and does anyone upstairs know that?

Engine-room questions:

- Which components, data stores, and contracts change?
- What does on-call see at 3am when it fails?
- What is the migration path from what runs today, including the awkward
  middle state where both exist?
- What has to be true about the team for this to be operated well?

Translate between floors. Do not relay. "We need Kafka" is engine-room
vocabulary that the penthouse cannot price. "We can add a new consumer of
order data in a day instead of a quarter, at the cost of a second system to
operate" is a trade-off both floors can argue about.

## Architecture is selling options

Deferring a decision has value when the future is uncertain and the cost of
keeping the door open is low. That value is an option, and options have a
premium. Sometimes the premium is worth it, sometimes it is gold-plating.

For every option considered ask:

- What does it cost to keep this door open? An abstraction layer, a second
  deployment, a slower build, a team that has to understand both.
- How likely is it that we walk through the door? If nobody can name the
  scenario, the premium is waste.
- How much does it cost to undo? Cheap undo means decide fast and move.
  Expensive undo means this is where the analysis budget goes.

"Make it configurable" and "put an interface in front of it" are option
purchases. Price them like one.

## "Is this a good architecture?" is not a question

The answer is always "good for what?" A design is good relative to the
stressors it survives and the price paid to survive them. So the deliverable
of architecture work is not the diagram. It is the set of decisions, each
with the alternatives that were considered and the reason they lost. A
document with a decision and no losers is a description, not a decision.

Distill. A trade-off the reader cannot hold in their head is not a trade-off
they can act on. One sentence per axis: "we give up X to get Y."

## Non-requirements

Nobody writes down the things that matter most: how fast this area of the
business changes, who will operate the thing, which team owns the data, how
the organization is structured, what the incentives are. Architects deal
with the non-requirements. Ask for them explicitly at rung 1.

Rate of change beats current position. A system that is slow to change is
worse than a system that is slightly wrong but fast to change, in any part
of the business that is still moving. Ask where the change velocity is
needed before asking what the structure should be.

## Coupling has a price on both sides

Loose coupling is not free. It obfuscates the system structure, adds
overhead, and makes the flow harder to follow. What it buys is the ability
to change one side without propagating the change. Tight coupling is also
not free, but it is simpler to see and cheaper to run.

Do not pick the least coupling. Pick the coupling you can afford in the
places where independent change is actually needed. Everywhere else, the
simpler thing.

When an option adds an integration seam, ask which change it lets you make
alone that you could not make alone before, and whether that change is one
anyone plans to make.

## Organizational forces

Conway holds: the system will mirror the communication structure. A boundary
that no team owns will rot. A boundary that splits one team in half will be
crossed constantly.

Project incentives point away from architecture. Scope and deadline are
rewarded now; structure that pays off later is not. When the analysis says
"this saves us in year two" ask who in the room is measured on year two.

New technology does not solve problems. It punishes bad habits. Before
recommending a new platform, broker, or database, name the habit that made
the current one painful and check whether the new one lets the habit
continue.

Platforms go where the bottleneck is. When a proposal centralizes something,
ask whether that is the current bottleneck or last year's.

## Elevator anti-patterns

Recognize these in your own draft:

- Justified after the fact: a decision followed by reasons, with no losing
  alternative that was seriously explored.
- One-floor architecture: a slide deck that never touched the engine room,
  or a code-level design nobody upstairs can price.
- Configurability as avoidance: "we'll make it a setting" instead of
  deciding.
- Vendor-deck architecture: the option list is the vendor's feature list.
- Resilience everywhere: every stressor survived, no price stated, nobody
  asked whether the penthouse cares.
- Reinvention: an existing pattern renamed. Name the original, state the
  difference, or drop the new name.

## Elevator pass, rung 5 checklist

Run this over your own stressor table and pricing:

1. For each stressor that drove a design choice: does anyone on the
   penthouse floor care if it happens? If not, cut the choice or mark it as
   optional.
2. For each option-keeping abstraction: name the scenario in which the
   option is exercised. No scenario, no abstraction.
3. For each "loosely coupled" seam: name the independent change it enables
   and who plans to make it.
4. For the recommended option: who is measured on the year in which it pays
   off?
5. Can the accepted trade-off be said in one sentence a CFO would understand?
