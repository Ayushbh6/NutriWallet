# Week 5 — Launch & Polish

## Goals
- Deploy backend and frontend to production
- Create demo video and launch materials
- Launch on Reddit, Hacker News, Twitter
- Collect feedback and iterate

## Tasks

### 1. Production Deployment

#### Backend (Railway / Render)
- Dockerfile for FastAPI app
- Environment variables configured:
  - `OPENAI_API_KEY`
  - `SUPABASE_URL`
  - `SUPABASE_SECRET_KEY` (sb_secret_... - backend only)
  - `REDIS_URL` (for Celery)
- Health check endpoint verified
- Celery worker deployed for scheduled scraping
- Rate limiting on `/api/scrape/trigger`

#### Frontend (Vercel)
- Next.js deployment configuration
- Environment variables: `NEXT_PUBLIC_API_URL`
- Custom domain (optional): nutriwallet.app or similar
- Analytics setup (Vercel Analytics or Plausible)

#### Database (Supabase)
- Production database with seed data
- Row Level Security (RLS) policies if needed
- Backup strategy configured

### 2. Pre-Launch Testing
- End-to-end test on production:
  - €50/Vienna meal plan generation
  - £40/London meal plan generation
  - ₹2000/Mumbai meal plan generation
- Performance check: < 30 second response time
- Error handling: Test with invalid inputs
- Mobile testing on real devices

### 3. Demo Video
- **Script**:
  1. Problem statement (30 sec): "Most meal planners ignore your budget..."
  2. Solution demo (60 sec): Show the app in action
  3. Results (30 sec): Show generated meal plan, shopping list
  4. Call to action (15 sec): "Try it free at..."
- Record with Loom or screen recording
- Keep under 2 minutes
- Add captions for accessibility

### 4. Launch Materials

#### Landing Page Copy
- Headline: "Eat healthy on any budget"
- Subhead: "Tell us your weekly budget, we'll optimize your nutrition"
- Key features: Budget-first, real prices, optimized nutrition
- Social proof (after launch): User testimonials, usage stats

#### Social Media Posts
- **Twitter/X Thread**:
  - Problem → Solution → Demo GIF → Link
  - Tag relevant accounts (@IndieHackers, etc.)
- **Reddit Posts** (prepare for each subreddit):
  - r/EatCheapAndHealthy: Focus on savings
  - r/mealprep: Focus on convenience
  - r/Frugal: Focus on budget optimization
  - r/SideProject: Focus on building journey
- **Hacker News**:
  - "Show HN: NutriWallet – Budget-first meal planning with AI"
  - Technical angle: Agent architecture, optimization

### 5. Launch Execution

#### Day 1: Soft Launch
- Post on Twitter with demo video
- Share with friends/family for initial feedback
- Monitor for critical bugs

#### Day 2: Reddit Launch
- Post on r/EatCheapAndHealthy (largest audience)
- Engage with comments, answer questions
- Note feedback themes

#### Day 3: Hacker News
- Submit Show HN post
- Be available to answer technical questions
- Highlight the agentic architecture angle

#### Day 4-5: Follow-up
- Post on remaining subreddits
- Indie Hackers community post
- Respond to all feedback

### 6. Feedback Collection
- **In-App Feedback**:
  - Simple "Was this helpful?" after meal plan
  - Optional email capture for updates
- **Track Metrics**:
  - Meal plans generated (total, by city)
  - Completion rate (start → finish)
  - Return users
  - Error rate
- **User Interviews**:
  - Reach out to active users
  - 15-minute calls to understand pain points
  - "Would you pay for this?" validation

### 7. Post-Launch Iteration
- Fix critical bugs immediately
- Prioritize feedback by frequency
- Quick wins: UI polish, error messages
- Plan Week 6 based on learnings

## Checkpoints
- [ ] Backend deployed and responding on production URL
- [ ] Frontend deployed and accessible
- [ ] Demo video recorded and uploaded
- [ ] Reddit posts drafted for each subreddit
- [ ] Hacker News post drafted
- [ ] Analytics tracking working
- [ ] Feedback mechanism in place

## Verification
- Production URL returns meal plan successfully
- Demo video plays without issues
- At least 1 Reddit post published and getting engagement
- Feedback form captures responses
- No critical errors in production logs

## Success Metrics (MVP)
From Technical Architecture:
- [ ] Successfully scrape 50+ products from 4 stores
- [ ] Generate a valid €50/week meal plan for Vienna
- [ ] < 30 second response time for meal plan generation
- [ ] 5+ test users complete a full week using the plan
- [ ] At least 1 "would pay for this" response

## Launch Channels Summary
| Channel | Audience | Angle |
|---------|----------|-------|
| Twitter/X | Tech/Indie | Building journey, AI agents |
| r/EatCheapAndHealthy | 2.5M | Budget eating, savings |
| r/mealprep | 1.5M | Convenience, planning |
| r/Frugal | 2M | Budget optimization |
| r/SideProject | Builders | Technical journey |
| Hacker News | Tech | Agentic AI, optimization |
| Indie Hackers | Founders | Validation, growth |

