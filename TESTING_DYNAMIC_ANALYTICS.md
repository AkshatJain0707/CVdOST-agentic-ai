# Testing Guide: Dynamic Analytics Implementation

## Quick Start

### Prerequisites
- Backend running: `uvicorn backend.main:app --reload`
- Frontend running: `streamlit run frontend.py`
- Valid OpenAI API key in `.env`
- spaCy model installed (or it will fallback gracefully)

## Testing Checklist

### ✅ Session State Initialization
1. Start Streamlit app
2. Open DevTools Console (F12)
3. Verify no errors in console
4. Each tab should load without errors

**Expected Behavior:** All tabs accessible, Analytics shows "No analysis data yet" message

---

### ✅ First Analysis Workflow
1. Navigate to **📊 Dashboard Overview** tab
2. Upload a resume file (PDF or DOCX)
3. Paste a job description
4. Click **"Analyze Resume"** button
5. Wait for analysis to complete
6. Verify you see:
   - ✅ Success message
   - ✅ Three key metrics (ATS, Semantic, Skill Fit)
   - ✅ Scoring breakdown chart
   - ✅ Improvement suggestions
   - ✅ Tip about Analytics tab

**Expected Scores:** Typically between 40-95% depending on resume-JD match

---

### ✅ Analytics Tab - Score Overview
1. After analysis completes, navigate to **📈 Analytics & Insights**
2. Click **"📊 Score Overview"** tab
3. Verify you see:
   - ✅ **Performance Funnel** chart (with real scores)
   - ✅ **Resume Fitness Radar** chart (multi-dimensional)
   - ✅ **Score Components Breakdown** (metrics cards)

**Key Check:** All scores should match those shown in Dashboard

---

### ✅ Analytics Tab - Skill Gap Analysis
1. In Analytics, click **"🎯 Skill Gap Analysis"** tab
2. Verify two columns appear:
   - ✅ Left: "✅ Matched Skills" with count
   - ✅ Right: "⚠️ Missing Skills (Gap)" with count
3. Check that:
   - ✅ Up to 10 skills shown per column
   - ✅ "... and X more" text if count > 10
   - ✅ **Skill Coverage Distribution** pie chart appears

**Expected Data:** Green for matched, Red for gaps

---

### ✅ Analytics Tab - Recommendations
1. In Analytics, click **"💡 Recommendations"** tab
2. Verify:
   - ✅ Success count: "X recommendations to improve your match"
   - ✅ Each recommendation in green insight box
   - ✅ Score interpretation cards with emoji indicators (🟢 🟡 🔴)
   - ✅ Three interpretation cards: ATS, Semantic, Skill Fit

**Expected Indicators:**
- 🟢 Score ≥ 75%
- 🟡 Score 50-74%
- 🔴 Score < 50%

---

### ✅ Analytics Tab - Comparison (Single Analysis)
1. In Analytics, click **"📈 Comparison"** tab
2. For first analysis, should see:
   - ℹ️ Message: "Perform multiple analyses to see comparison trends!"

---

### ✅ Multiple Analyses & Comparison
1. Return to **📊 Dashboard** tab
2. Analyze with **different resume or JD**
3. Wait for completion
4. Return to **📈 Analytics & Insights**
5. Verify in **"📈 Comparison"** tab:
   - ✅ Info message shows: "2 analyses performed"
   - ✅ **Line chart** shows score progression over time
   - ✅ **History table** displays all analyses with timestamps

**Expected Behavior:** Line chart with 3 lines (ATS, Semantic, Skill Fit) going through 2 data points

---

### ✅ Report Download - No Analysis
1. Navigate to **📥 Download Report** tab
2. Verify message shows:
   - ⚠️ "No analysis data available yet"
   - ℹ️ Instructions to perform analysis first

---

### ✅ Report Download - Text Export
1. After analysis, navigate to **📥 Download Report**
2. Click **"📊 Download Full AI Report"** button
3. Verify file downloads (should be named `ResuMate_Report_YYYYMMDD_HHMMSS.txt`)
4. Open downloaded file and check contains:
   - ✅ Executive Summary with all 3 scores
   - ✅ Assessment indicator (🟢 🟡 🔴)
   - ✅ Detailed Score Breakdown
   - ✅ Skill Analysis section
   - ✅ Recommendations section
   - ✅ Score Guidance

---

### ✅ Report Download - JSON Export
1. In **📥 Download Report** tab
2. Click **"📦 Export as JSON"** button
3. Verify file downloads (should be named `ResuMate_Data_YYYYMMDD_HHMMSS.json`)
4. Open with text editor and verify:
   - ✅ Valid JSON format (can parse without errors)
   - ✅ Contains all analysis data
   - ✅ Includes matcher, ats, orchestration results

---

### ✅ Report Download - CSV Export
1. In **📥 Download Report** tab
2. Click **"📊 Export Scores as CSV"** button
3. Verify file downloads (should be named `ResuMate_Scores_YYYYMMDD_HHMMSS.csv`)
4. Open with spreadsheet app and verify:
   - ✅ Header row: "Metric" and "Score"
   - ✅ Data rows: ATS Score, Semantic Match, Skill Fit, all components
   - ✅ Scores match those shown in UI

---

## Edge Cases to Test

### Test 1: Resume with Perfect Match
**Setup:** Use a resume that exactly matches all JD keywords

**Expected Results:**
- All scores high (80%+)
- Few or no recommendations
- Minimal skill gaps
- Green indicators (🟢) across the board

---

### Test 2: Resume with Poor Match
**Setup:** Use a resume from completely different field

**Expected Results:**
- Lower scores (40-60%)
- Multiple recommendations
- Large skill gaps
- Yellow/Red indicators (🟡 🔴)
- Many missing skills

---

### Test 3: Multiple Analyses with Different JDs
**Setup:** Analyze same resume against 2-3 different job descriptions

**Expected Results:**
- Analytics show different scores for each analysis
- Comparison chart shows trend (improving/declining scores)
- History table shows all analyses with different timestamps

---

### Test 4: Very Long Skill Lists
**Setup:** Resume with 30+ skills, JD with 40+ skills

**Expected Results:**
- "... and X more" text appears under skills
- Pie chart still displays correctly
- No UI layout breakage

---

### Test 5: Missing Optional Data
**Setup:** If backend returns incomplete data

**Expected Results:**
- No errors in console
- Fallback messages shown where data unavailable
- App continues to function
- Charts don't break

---

## Common Issues & Troubleshooting

### Issue: "No analysis data available" after clicking Analyze
**Solution:** 
- Check backend logs: `data/logs/` directory
- Verify OpenAI API key is valid in `.env`
- Check network tab in DevTools for API errors
- Try simple resume/JD first

### Issue: Charts not showing in Analytics
**Solution:**
- Refresh page (Ctrl+R)
- Clear Streamlit cache: `streamlit cache clear`
- Check browser console for JavaScript errors
- Verify data exists: Check the Dashboard tab first

### Issue: Scores don't match between tabs
**Solution:**
- This shouldn't happen with session state
- Check if you're using different browsers
- Verify data structure: Open DevTools, check Streamlit session state
- Clear browser cache and refresh

### Issue: Export button not working
**Solution:**
- Verify browser allows downloads
- Check file isn't already open
- Try different file format
- Check browser console for errors

### Issue: "KeyError" or "AttributeError" in Streamlit
**Solution:**
- Check backend is running and responding
- Verify API response format in browser DevTools
- Look at backend logs for parsing errors
- Try fresh analysis

---

## Performance Testing

### Expected Load Times
- Dashboard analysis: 10-30 seconds
- Analytics tab load: <1 second
- Report generation: <2 seconds
- File download: Instant

### Memory Usage
- Session state size: < 5MB for typical analysis
- Frontend RAM: Normal Streamlit usage (~200-300MB)

### Concurrent Users
- Should handle 5-10 simultaneous users on local deployment
- Scale up backend for production use

---

## Success Criteria

✅ **All tests pass if:**
1. No errors in browser console or Streamlit logs
2. All charts render with real data
3. Session state persists across tab navigation
4. Multiple analyses track correctly in history
5. All export formats work and download correctly
6. Scores consistent across Dashboard and Analytics
7. Responsive design works on different screen sizes

✅ **Dynamic Analytics is ready for production when:**
- All items above pass
- Users can complete full workflow: Analyze → View Analytics → Download Report
- No performance issues with multiple analyses
- Edge cases handled gracefully

---

## Quick Regression Test (< 5 minutes)

```
1. Upload resume + paste JD (30s)
2. Analyze (15-20s)
3. Navigate to Analytics (1s)
   ✓ Check 4 tabs load
   ✓ Verify all charts show data
4. Go to Report (1s)
   ✓ Download text file (1s)
   ✓ Open file in notepad
   ✓ Verify content looks good
5. Total: ~4-5 minutes for full regression
```

---

## Acceptance Criteria

Users can:
- [ ] See dynamic analytics after any analysis
- [ ] View 4 different analytics perspectives
- [ ] Track multiple analyses over time
- [ ] Export results in 3 formats
- [ ] Understand score interpretation
- [ ] Get actionable recommendations
- [ ] No errors or broken UI
- [ ] Responsive on mobile/tablet

**When all checked: ✅ Implementation complete and production-ready**