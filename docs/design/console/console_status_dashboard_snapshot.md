# Console Status Dashboard Snapshot

This document explains the integration of the meta-strategic domain dashboard snapshot into the console `status` command within the MVP Text Console.

## Overview

The `status` command has been updated to provide a unified meta-strategic report. In addition to current floor and tactical pressures, it now includes a **Domain Dashboard Snapshot** that aggregates evidence from all core engine subsystems.

This ensures that the player has a cognitively readable overview of their survival flexibility across multiple tactical domains (combat, traversal, resources, and history).

## Integrated Evidence

The status payload now includes a structured `dashboard_snapshot` containing:

1.  **Pressure Summary**: A weighted aggregation of Combat, Traversal, Escape, Mutation, Repair, and Capacity pressures.
2.  **Equipment Summary**: Counts of damaged items and remaining repair materials.
3.  **Resource Summary**: Total gold, ash potions, and rare materials in the inventory.
4.  **Route Summary**: Tactical movement history (routes traversed and escape failures).
5.  **Residue Summary**: Recursive history of the Domain (mutations triggered and marks remaining).
6.  **Recoverability Status**: A heuristic check confirming if the player is under critical survival pressure.

## Strategic Cognition

By surfacing the dashboard snapshot during status checks, the "Tower" enables the player to move beyond reactive tactical play toward proactive meta-strategic management. A player can now see how their accumulated inventory weight (Capacity Pressure) is impacting their risk of failing a retreat (Escape Risk), or how their gear's deteriorating condition (Repair Burden) is increasing the total hazard of the journey.

## Identity Preservation

*   **Non-Modifying**: Checking status remains a strictly read-only operation. It gathers and summarizes evidence without altering the game or tower state.
*   **Bounded Visibility**: Information is derived strictly from the current known session state. No "hidden" future information or unexplored topography is revealed.
*   **Audit Trail**: The inclusion of the snapshot in the status command ensures that meta-strategic state is granularly recorded in session transcripts for post-run analysis.
