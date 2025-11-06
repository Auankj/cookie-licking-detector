# Cookie-Licking Detector - User Guide

**How to Use the Cookie-Licking Detector System**

A comprehensive guide for open-source contributors and repository maintainers.

---

## Table of Contents

1. [What is Cookie Licking?](#what-is-cookie-licking)
2. [How the System Works](#how-the-system-works)
3. [For Contributors (Issue Claimers)](#for-contributors-issue-claimers)
4. [For Repository Maintainers](#for-repository-maintainers)
5. [Common User Flows](#common-user-flows)
6. [Notifications & Nudges](#notifications--nudges)
7. [Understanding Claim Status](#understanding-claim-status)
8. [Best Practices](#best-practices)
9. [FAQ](#faq)

---

## What is Cookie Licking?

**Cookie licking** is when someone claims to work on an open-source issue but never follows through, preventing others from contributing. It's like licking a cookie at a party so no one else will eat it! 🍪

### The Problem:
1. 👤 **Contributor**: "I'll work on this!" (claims the issue)
2. ⏰ **Days pass...** (no progress, no updates)
3. 😔 **Other contributors**: Can't contribute (issue appears taken)
4. 📉 **Result**: Issue sits stale, project suffers

### Our Solution:
The Cookie-Licking Detector **automatically monitors** issue claims and:
- ✅ Detects when someone claims an issue
- ✅ Tracks their progress
- ✅ Sends friendly nudges if inactive
- ✅ Auto-releases stale claims
- ✅ Keeps projects moving forward

---

## How the System Works

### 🤖 Automated Detection

The system uses AI-powered pattern matching to detect claims like:

**Explicit Claims:**
- "I'll work on this"
- "I can take this on"
- "Let me handle this issue"
- "I'll submit a PR for this"

**Implicit Claims:**
- "Working on a fix"
- "I'm on it"
- "I've started implementing this"

**Assignment Claims:**
- User is officially assigned to the issue
- User mentions they're assigned

### 📊 Confidence Scoring

Each claim gets a confidence score (0-100):
- **75-100**: High confidence (explicit claim)
- **50-74**: Medium confidence (implicit claim)
- **0-49**: Low confidence (ambiguous)

Only claims above the repository's threshold (default: 75) trigger monitoring.

### ⏱️ Timeline

Once a claim is detected:

```
Day 0: Claim Detected
   ↓
Day 7: First Nudge (if no activity)
   ↓
Day 10: Second Nudge (if still no activity)
   ↓
Day 14: Auto-Release (claim freed for others)
```

**Configurable per repository:**
- Grace period: 3-30 days
- Nudge count: 0-5 nudges
- Nudge intervals: customizable

---

## For Contributors (Issue Claimers)

### How It Affects You

#### ✅ **When You Claim an Issue:**

1. **Comment on the issue** with your intention:
   ```
   "I'll work on this issue and submit a PR by Friday"
   ```

2. **System detects your claim** (within seconds)
   - You'll see your claim on the public dashboard
   - Grace period starts (typically 7 days)

3. **Show progress** to avoid nudges:
   - Comment updates on the issue
   - Push commits to your branch
   - Reference the issue in commits
   - Keep communication open

#### 📧 **Receiving Nudges:**

If you haven't shown activity, you'll receive **friendly reminders**:

**First Nudge (Day 7):**
```
Hi @johndoe! 👋

We noticed you claimed issue facebook/react#1234 a week ago.
Just checking in - are you still working on this?

If you need help or more time, let us know!
If you're no longer able to work on it, no problem - just let us know
so others can contribute.

Thanks for being part of the community! 🚀
```

**Second Nudge (Day 10):**
```
Hi @johndoe,

Quick follow-up on facebook/react#1234.
We haven't seen activity for 10 days.

Please provide an update within 4 days, or we'll release this issue
for other contributors.

We appreciate your interest! 💙
```

#### 🔓 **Auto-Release (Day 14):**

If no response after nudges:
```
Issue facebook/react#1234 has been released for other contributors.

@johndoe, you're welcome to reclaim it if you're ready to work on it!
Thanks for your understanding. 🙏
```

### How to Stay Active

✅ **Do this** to prevent auto-release:

1. **Comment regularly:**
   ```
   "Working on the implementation, about 50% done"
   "Hit a blocker with X, researching solutions"
   "PR will be ready by Tuesday"
   ```

2. **Push commits:**
   - Even work-in-progress commits count
   - Reference the issue: `git commit -m "feat: add feature for #1234"`

3. **Ask for help:**
   ```
   "Need help understanding the architecture - can someone review?"
   ```

4. **Request more time:**
   ```
   "This is more complex than expected, need another week"
   ```

5. **Be honest if you can't finish:**
   ```
   "Sorry, I'm too busy right now. Releasing this for others."
   ```

❌ **Don't do this:**
- Claim issues and disappear
- Ignore nudges
- Leave issues in limbo
- Claim multiple issues without delivering

---

## For Repository Maintainers

### Setting Up Your Repository

#### 1. **Register Your Repository**

**Via Web UI:**
1. Visit the dashboard: `http://your-domain.com/dashboard`
2. Click "Add Repository"
3. Enter repository details:
   - Repository: `owner/repo`
   - Grace Period: 7 days (default)
   - Nudge Count: 2 (default)
   - Detection Threshold: 75% (default)

**Via API:**
```bash
curl -X POST http://localhost:8000/api/v1/repositories \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "github_repo_id": 123456789,
    "owner_name": "facebook",
    "name": "react",
    "full_name": "facebook/react",
    "url": "https://github.com/facebook/react",
    "grace_period_days": 7,
    "nudge_count": 2,
    "claim_detection_threshold": 75
  }'
```

#### 2. **Configure Settings**

**Grace Period** (Days until first action):
- **3 days**: Fast-moving projects
- **7 days**: Standard (recommended)
- **14 days**: Complex issues
- **30 days**: Long-term projects

**Nudge Count** (Reminders before auto-release):
- **0**: No nudges (strict auto-release)
- **1**: Single warning
- **2**: Standard (recommended)
- **3-5**: Patient approach

**Detection Threshold** (Confidence score):
- **90-100**: Only explicit claims
- **75**: Balanced (recommended)
- **50-74**: Include implicit claims
- **0-49**: Everything (may have false positives)

#### 3. **Install GitHub Webhook**

**Automatic Setup:**
The system can auto-configure webhooks with GitHub API access.

**Manual Setup:**
1. Go to `https://github.com/owner/repo/settings/hooks`
2. Click "Add webhook"
3. Configure:
   - **Payload URL**: `https://your-domain.com/api/v1/webhooks/github`
   - **Content type**: `application/json`
   - **Secret**: (your webhook secret)
   - **Events**: 
     - ✅ Issue comments
     - ✅ Issues
     - ✅ Pull requests
     - ✅ Pull request reviews

4. Click "Add webhook"

### Monitoring Your Repository

#### **Dashboard View**

Access at: `http://your-domain.com/dashboard/repositories`

**You'll see:**
```
Repository: facebook/react
Status: ✅ Healthy

Statistics:
├─ Total Issues: 150
├─ Open Issues: 85
├─ Active Claims: 15
├─ Completed Claims: 45
├─ Expired Claims: 3
├─ Completion Rate: 75.0%
└─ Avg Claim Duration: 4.2 days

Health Score: 85.5/100
Last Activity: 2 minutes ago
```

#### **View All Claims**

Access at: `http://your-domain.com/claims?repository=facebook/react`

**Filter options:**
- By status: Active, Released, Completed, Expired
- By user: See all claims by a contributor
- By date: Last 7 days, 30 days, all time

#### **Claim Details**

Click any claim to see:
```
Claim #42
Status: Active (Day 5/14)

Issue: facebook/react#1234 - Add dark mode support
Claimed by: @johndoe
Confidence: 95% (explicit claim)
Claim text: "I'll work on this issue"

Timeline:
├─ Nov 1, 10:00 AM - Claim detected
├─ Nov 3, 2:30 PM - Commit pushed (activity)
├─ Nov 4, 4:15 PM - Comment posted (activity)
└─ Nov 8, 10:00 AM - First nudge scheduled

Next Action: First nudge in 3 days
Auto-Release: In 9 days (if no activity)
```

### Manual Actions

#### **Release a Claim Early**

If a contributor requests release or you need to free an issue:

```bash
# Via API
curl -X POST http://localhost:8000/api/v1/claims/42/release \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"reason": "User requested release"}'
```

**Via UI:**
1. Go to claim details
2. Click "Release Claim"
3. Select reason
4. Confirm

#### **Extend Grace Period**

For complex issues needing more time:

```bash
curl -X PUT http://localhost:8000/api/v1/claims/42 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"grace_period_extension_days": 7}'
```

#### **Adjust Repository Settings**

```bash
curl -X PUT http://localhost:8000/api/v1/repositories/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "grace_period_days": 10,
    "nudge_count": 3,
    "claim_detection_threshold": 80
  }'
```

### Notification Settings

**Configure how maintainers get notified:**

```json
{
  "notification_settings": {
    "email_notifications": true,
    "daily_summary": true,
    "weekly_report": true,
    "immediate_alerts": {
      "new_claims": false,
      "expired_claims": true,
      "high_activity": true
    },
    "email_frequency": "daily",
    "recipients": [
      "maintainer@example.com",
      "team@example.com"
    ]
  }
}
```

---

## Common User Flows

### Flow 1: Successful Contribution

```
📝 Contributor comments: "I'll work on this"
   ↓
🤖 System detects claim (95% confidence)
   ↓
💻 Contributor pushes commits regularly
   ↓
📬 Contributor posts updates
   ↓
✅ PR submitted and merged
   ↓
🎉 Claim marked as completed
```

**Outcome:** ✅ Issue resolved, contributor gets credit, everyone happy!

---

### Flow 2: Contributor Needs More Time

```
📝 Contributor claims issue
   ↓
⏰ Day 7: First nudge sent
   ↓
💬 Contributor responds: "Need 3 more days"
   ↓
⏱️ System extends grace period
   ↓
✅ PR submitted on day 10
```

**Outcome:** ✅ Flexibility provided, issue still resolved!

---

### Flow 3: Abandoned Claim (Auto-Release)

```
📝 Contributor claims issue
   ↓
😴 No activity for 7 days
   ↓
📧 First nudge sent - no response
   ↓
😴 Still no activity
   ↓
📧 Second nudge sent - no response
   ↓
🔓 Day 14: Auto-release
   ↓
🆕 Issue available for new contributors
```

**Outcome:** ✅ Issue freed, project keeps moving!

---

### Flow 4: Honest Release

```
📝 Contributor claims issue
   ↓
🤔 Realizes it's too complex
   ↓
💬 Comments: "Sorry, this is beyond my skill level"
   ↓
🔓 Claim released immediately
   ↓
🆕 Other contributors can take over
```

**Outcome:** ✅ Honesty appreciated, no time wasted!

---

### Flow 5: False Positive

```
📝 Someone comments: "This looks interesting"
   ↓
🤖 System detects potential claim (60% confidence)
   ↓
⚠️ Below threshold (75%) - ignored
   ↓
✅ No monitoring triggered
```

**Outcome:** ✅ Casual comments don't trigger the system!

---

## Notifications & Nudges

### Email Notifications

#### **For Contributors:**

**Claim Detected:**
```
Subject: Issue Claim Detected - facebook/react#1234

Hi @johndoe,

We detected that you claimed issue facebook/react#1234:
"Add dark mode support"

Your comment: "I'll work on this issue"
Confidence: 95%

Grace Period: 7 days
Expected completion: November 12, 2025

To avoid automatic release:
✓ Post regular updates
✓ Push commits referencing the issue
✓ Ask questions if blocked

View claim: https://cookie-detector.com/claims/42

Good luck! 🚀
```

**First Nudge:**
```
Subject: Progress Check - facebook/react#1234

Hi @johndoe,

Just checking in on facebook/react#1234.
You claimed this issue 7 days ago.

We haven't detected activity since November 1.

Still working on it? Let us know!
Need help? Ask in the issue comments.
Can't continue? No problem - just let us know.

Next nudge: November 12
Auto-release: November 15

View claim: https://cookie-detector.com/claims/42
```

**Auto-Release Warning:**
```
Subject: Final Reminder - facebook/react#1234

Hi @johndoe,

This is a final reminder about facebook/react#1234.

No activity detected for 10 days.
Auto-release scheduled: November 15 (in 4 days)

Please provide an update to keep this claim active.

View claim: https://cookie-detector.com/claims/42
```

**Released:**
```
Subject: Claim Released - facebook/react#1234

Hi @johndoe,

facebook/react#1234 has been released for other contributors.

You're welcome to reclaim it if you're ready to work on it.
Thanks for your interest in the project!

View issue: https://github.com/facebook/react/issues/1234
```

#### **For Maintainers:**

**Daily Summary:**
```
Subject: Daily Activity Summary - facebook/react

Today's Activity:
├─ New Claims: 3
├─ Active Claims: 15
├─ Completed Claims: 2
├─ Expired Claims: 1
└─ Nudges Sent: 4

Top Contributors:
1. @johndoe (3 active claims, 85% completion rate)
2. @janedoe (2 active claims, 90% completion rate)

Issues Needing Attention:
⚠️ Issue #1230 - No activity for 12 days
⚠️ Issue #1245 - Approaching auto-release

View dashboard: https://cookie-detector.com/dashboard
```

**Weekly Report:**
```
Subject: Weekly Report - facebook/react

Week of Nov 1-7, 2025

Summary:
├─ New Claims: 12
├─ Completed: 8
├─ Expired: 2
├─ Completion Rate: 80%
└─ Avg Claim Duration: 5.2 days

Health Score: 85/100 (Healthy)

Trends:
📈 Completion rate up 5% from last week
📉 Avg duration down from 6.1 days

Top Contributors:
1. @contributor1 (4 completed, 100% rate)
2. @contributor2 (3 completed, 100% rate)

View full report: https://cookie-detector.com/reports/weekly
```

### In-App Notifications

**Notification Center** (when logged in):

```
🔔 Notifications (3 new)

📝 New claim detected on react#1234
   2 minutes ago

⏰ First nudge sent to @johndoe
   1 hour ago

✅ Claim #40 completed by @janedoe
   3 hours ago

🔓 Claim #38 auto-released
   Yesterday
```

---

## Understanding Claim Status

### Status Definitions

#### 🟢 **Active**
- Claim is currently being worked on
- Within grace period
- Monitoring ongoing
- Can receive nudges

#### 🟡 **Released**
- Claim was released (auto or manual)
- Issue available for others
- Contributor can reclaim
- No longer monitored

#### ✅ **Completed**
- Issue was successfully resolved
- PR merged or issue closed
- Contributor gets credit
- Archived for statistics

#### ⏰ **Expired**
- Auto-released after grace period
- No response to nudges
- Moved to released status
- Counted in statistics

### Status Transitions

```
        Claim Detected
              ↓
         🟢 ACTIVE
         ↙    ↓    ↘
       /      |      \
Activity   Manual   Deadline
Continues  Release  Reached
      |      |        |
      |      ↓        ↓
      |  🟡 RELEASED  |
      |              /
      |  No Response/
      |   No Activity
      ↓      ↓
   ✅ COMPLETED
```

---

## Best Practices

### For Contributors

✅ **DO:**
1. **Be realistic** - Only claim what you can deliver
2. **Communicate early** - Post updates, ask questions
3. **Show progress** - Commit often, even WIP
4. **Be honest** - Release if you can't finish
5. **Respond to nudges** - They're friendly reminders
6. **Check before claiming** - See if issue is already claimed
7. **Focus on quality** - Better to do one well than many poorly

❌ **DON'T:**
1. **Claim and vanish** - Stay engaged
2. **Ignore nudges** - Respond to communication
3. **Over-commit** - Don't claim 10 issues at once
4. **Be defensive** - Nudges aren't criticism
5. **Ghost the maintainers** - Communication is key

### For Maintainers

✅ **DO:**
1. **Set appropriate grace periods** - Match your project pace
2. **Be patient** - Contributors have lives
3. **Provide clear guidelines** - Document contribution process
4. **Thank contributors** - Appreciation goes a long way
5. **Monitor dashboard** - Stay aware of claim health
6. **Adjust thresholds** - Fine-tune based on experience
7. **Communicate policy** - Add to CONTRIBUTING.md

❌ **DON'T:**
1. **Be too aggressive** - 3-day grace period might be harsh
2. **Ignore the system** - Check dashboard regularly
3. **Disable nudges** - They help contributors stay on track
4. **Micro-manage** - Trust the automated process
5. **Punish honesty** - Thank contributors who release early

---

## FAQ

### General Questions

**Q: How does the system detect claims?**  
A: We use AI-powered natural language processing to analyze comments for claim patterns. We look for phrases like "I'll work on this", "I can handle this", etc.

**Q: What if I just asked a question, not claimed the issue?**  
A: Our system uses confidence scoring. Questions like "Can I work on this?" get lower scores and won't trigger monitoring unless they're very explicit.

**Q: Can I see all claims on a repository?**  
A: Yes! Visit `https://cookie-detector.com/claims?repository=owner/repo` - it's public and transparent.

**Q: Is my data private?**  
A: Claim data is public (it's from public GitHub issues). Your email is private. We don't sell or share your data.

---

### For Contributors

**Q: What counts as "activity"?**  
A: 
- Comments on the issue
- Commits referencing the issue
- PR drafts or submissions
- Any interaction with the issue

**Q: I'm working but haven't committed yet - what should I do?**  
A: Post a comment! "Working on the implementation, will push commits this week" counts as activity.

**Q: Can I claim multiple issues?**  
A: Yes, but be realistic. Active claims affect your completion rate, which is visible to maintainers.

**Q: What if I go on vacation?**  
A: Comment before you leave: "Going on vacation Nov 10-17, will resume work after." We'll extend your grace period.

**Q: How do I reclaim a released issue?**  
A: Just comment again! "I'm ready to work on this now" will create a new claim.

**Q: Do I get penalized for auto-release?**  
A: No penalties, but it affects your completion rate statistic. Honest communication is always better.

---

### For Maintainers

**Q: Can I disable the system for specific issues?**  
A: Yes, label issues with `no-claim-detection` to exclude them from monitoring.

**Q: What if someone legitimately needs more time?**  
A: You can manually extend grace periods, or the contributor can request extension in comments.

**Q: Can I manually release a claim?**  
A: Yes, via the dashboard or API. Useful for emergency situations.

**Q: What happens if the system makes a mistake?**  
A: You can manually override any decision. Also, report false positives to help improve our AI.

**Q: Does this work with issue assignments?**  
A: Yes! GitHub assignments automatically create high-confidence claims.

**Q: Can I see statistics for contributors?**  
A: Yes, the dashboard shows completion rates, active claims, and history for all contributors.

---

### Technical Questions

**Q: What technologies power this?**  
A: FastAPI (Python), PostgreSQL, Redis, AI/ML for pattern detection, GitHub webhooks.

**Q: Is it open source?**  
A: Check our repository for licensing information.

**Q: Can I self-host this?**  
A: Yes! See our deployment documentation.

**Q: How real-time is the detection?**  
A: Claims are detected within seconds via GitHub webhooks.

**Q: What's the API rate limit?**  
A: 1000 requests/hour for authenticated users, 100/hour for anonymous.

**Q: Can I integrate this with my CI/CD?**  
A: Yes! We have a full REST API - see API_ENDPOINTS_GUIDE.md

---

## Support & Resources

### Getting Help

**Contributors:**
- 📧 Email: support@cookie-detector.com
- 💬 Discord: [Join our community]
- 📖 Docs: https://docs.cookie-detector.com

**Maintainers:**
- 📧 Priority support: maintainers@cookie-detector.com
- 📞 Video calls: Schedule via Calendly
- 📖 Admin docs: https://docs.cookie-detector.com/admin

### Useful Links

- 🏠 **Homepage**: https://cookie-detector.com
- 📊 **Public Dashboard**: https://cookie-detector.com/dashboard
- 📚 **API Docs**: https://cookie-detector.com/docs
- 🐙 **GitHub**: https://github.com/cookie-detector
- 🐛 **Report Issues**: https://github.com/cookie-detector/issues
- 💡 **Feature Requests**: https://github.com/cookie-detector/discussions

### Examples & Templates

**CONTRIBUTING.md Template:**
```markdown
## Issue Claims

This repository uses Cookie-Licking Detector to manage issue claims.

### How it works:
1. Comment on an issue to claim it
2. Show regular progress (commits, updates)
3. You'll receive friendly nudges if inactive
4. Claims auto-release after 14 days of inactivity

### Best practices:
- Only claim issues you can realistically complete
- Post updates regularly
- Ask for help if blocked
- Release claims you can't finish

View all claims: https://cookie-detector.com/claims?repository=owner/repo
```

---

## Quick Start Guide

### For Contributors (30 seconds)

1. **Find an issue** you want to work on
2. **Comment**: "I'll work on this"
3. **Start coding** and push commits
4. **Post updates** every few days
5. **Submit your PR**
6. **Celebrate!** 🎉

### For Maintainers (5 minutes)

1. **Sign up**: https://cookie-detector.com/register
2. **Add repository**: Dashboard → Add Repository
3. **Configure webhook**: GitHub Settings → Webhooks
4. **Customize settings**: Grace period, nudges, threshold
5. **Monitor dashboard**: Check weekly for health

---

**Happy Contributing! 🚀**

Remember: This system exists to help projects move forward and contributors succeed. Communication, honesty, and regular updates are the keys to smooth collaboration.

---

**Last Updated**: November 5, 2025  
**Version**: 1.0.0  
**Questions?** Email support@cookie-detector.com
