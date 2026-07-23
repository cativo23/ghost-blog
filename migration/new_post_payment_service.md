---
title: "Payment Service: One Interface for a Handful of Very Different Processors"
slug: payment-service-one-interface-many-processors
tags: ["payments", "architecture", "retrospective"]
created_at: 2026-07-23T00:00:00.000Z
updated_at: 2026-07-23T00:00:00.000Z
---

Somebody has to charge the cards. Nobody thinks about it until it doesn't work, and then everybody thinks about it at once.

This is my job at Blue Medical — I'm the one who ended up owning payments. I didn't design Payment Service because I woke up one day with an elegant idea about the Strategy Pattern. I got handed a mess — card numbers sitting in our own database, unencrypted — and told to make it stop being a mess. That's most of engineering, if you're honest about it. Nobody calls you in to admire something that already works.

## The way it was

Here's what "payments" looked like before I touched it. A single PHP script. Somebody — a person, with hands, at a keyboard — had to sit down and pick a range of Vivolife contracts, the health-membership plans Blue Medical sells across Guatemala and Costa Rica, and feed them through, 1 batch at a time, against a single payment processor. Charge them. Wait. Then fire off a separate request to generate the invoice, because god forbid the charge and the invoice happen in the same breath. Cards sat in the database in plain text, because nobody had gotten around to caring yet, or maybe they'd cared and just hadn't had the time, which amounts to the same thing when you're the one debugging it at midnight.

Charging $30k took about 9 hours. 9 hours, for a single batch job — a full workday spent watching a terminal scroll, waiting for one range of contracts to clear before you could start the next.

## First fix, not a clever one

The first thing I did wasn't clever, and it wasn't supposed to be. We needed to charge more, faster, with actual visibility into what was happening — and we needed it while the business kept charging, not after some graceful pause to rearchitect. So I moved it into a Laravel API and let Laravel's own queue system do what queues are for: batch the contracts, charge them 1 after another, automatically, without a human hovering over it like a nurse checking a drip. Same $30k. 2 hours instead of 9. Still 1 processor. Still 1 product. Still plaintext cards — that problem hadn't been touched yet, just the speed. It was progress the way finally throwing out the milk that's been bad for a week is progress — necessary, overdue, not glamorous.

## What's running now

Fixing the 9-hour fire is what bought the room to build the real thing later. You don't get to sit down and design a proper multi-gateway architecture while everyone's still waiting on a batch job to finish. What's running now is the 3rd version of this thing, and it's the one worth talking about. This is also where BlueMeds — medication delivered on a subscription — comes into the picture, alongside Vivolife, because the whole point of this version is that it doesn't care which product is asking.

No plaintext cards anymore. That part of the story is over, and good riddance. A card vault — VGS — holds the token, and only VGS ever sees the real number, handed straight to the processor at the edge. Our own database doesn't get to know. I like systems that don't get to know things they don't need to know. It's 1 less thing that can go wrong at 2 a.m., and 1 less thing I have to explain to somebody in a suit later.

VGS wasn't a coin flip. Our CTO had used them before somewhere else, and we still ran an actual comparison against the competition rather than taking that as the whole decision. VGS won on the merits — the prior experience just made the meeting shorter.

## The pattern underneath it

The real engineering underneath all of it is a Strategy Pattern — every payment processor gets its own class, its own little box, talking to 1 stable contract on the inside no matter what garbage protocol it's speaking on the outside. ISO 8583. SOAP and XML, which is its own special kind of penance. Plain REST, when you're lucky. Add a processor, write a new box for it. Don't touch the other boxes. That's the whole idea, and it sounds obvious written down like that, which is exactly why it's hard to actually do.

I know it's hard because I almost didn't do it, more than once. There's always a moment, mid-build, where the fast thing and the right thing split apart, and the fast thing is right there — just bolt this special case onto the shared class, ship it, deal with it later. I talked myself out of it every time with the same tired argument: it's cheaper to think about this now, while the thing is still new and nobody's money is actually moving through it yet, than it is to fix it once it's live and every change is a small act of terror. That argument held up. It usually does, if you actually listen to it instead of just hearing it.

## The stack I didn't get

I wanted to build the whole thing in NestJS, or Go, if I'm being honest about what I actually wanted. Neither of those would've been hard for me to pick up. But I wasn't the only 1 who'd have to live in this codebase, and the rest of the team knew Laravel and PHP, not Node, not Go. Handing a team a brand-new payment system and a brand-new language at the same time, and then possibly not being there myself down the road to help them through it — that's not ambition, that's just setting a trap for whoever's left holding it. So: Laravel. Not what I wanted. Still the right call, and I don't say that through gritted teeth. Some decisions you make for the codebase and some you make for the people who'll be stuck with it, and those aren't always the same decision.

## When a gateway has a bad day

The system moves everything async now — a queue, Horizon underneath it — so a processor having a bad day doesn't take the whole checkout flow down with it. There's a dashboard, because a queue with no visibility is just a black box where problems go to hide quietly until they're big enough to notice on their own. When a gateway is actually struggling — not "acting a little slow," genuinely struggling — somebody looks at that dashboard and manually switches the affected commerce over to a backup processor. Not automatically. A person decides. It doesn't happen often; this isn't a lever anyone's reaching for every week. I could wire up something that trips a circuit and reroutes on its own, and some engineer part of me still wants to. But which gateway a commerce runs on has cost and contract implications that are the business's call to make, not mine to automate out from under them. So the dashboard's job is to make the human fast, not to replace the human.

## Security, on a schedule

Security audits happen on a schedule here, OWASP-grade, not because something blew up and forced our hand. Defense-in-depth on the internal routes. Idempotency on the payment jobs, so a flaky network connection doesn't turn into a customer getting charged twice for the same thing, which is the kind of bug that ages a person. Network tokenization on top of the vault handles a different problem than the vault itself — the vault keeps our database from ever holding a real card number; network tokenization is what keeps a recurring charge working after a card gets reissued. Different layers, different jobs, both worth having. No matter how good the last audit looked, none of it stays secure by itself.

## What I'd redo

If I'm honest, it's testing. This got built fast, under real pressure, and the tests that check this service against the other systems calling into it came later, not from day 1. It's solid now. But "solid now" is a different sentence than "solid from the start," and payments are exactly the kind of system where that difference isn't cosmetic. A bug in a blog engine is embarrassing. A bug in a payment queue is somebody's money, sitting in the wrong state, at 3 a.m., with nobody around to notice until a customer does.

## Where it landed

I built this alone. It runs real billing now, across BlueMeds and Vivolife, across 2 countries, moving something like 15x the volume of the old $30k/2-hour run — in 2 to 3 hours now, depending on how fast the processors themselves respond, since that's the actual bottleneck these days, not us. Adding a new gateway is a class and a config entry now, not an event that makes everybody nervous. What's still missing — better monitoring, the kind of resilience patterns that come with a system that's actually grown into calling itself a microservice architecture instead of just 2 services and a prayer — is on the roadmap. Not a blind spot. Just not built yet.
