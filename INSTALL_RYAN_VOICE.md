# Installing Microsoft Ryan (British Male Voice)

## Current Status
Your system has **Microsoft Hazel (British female)** which Alfred will now use as a temporary fallback.

To get the proper **Ryan (British male)** voice that Alfred prefers:

## Installation Steps

1. **Open Windows Settings**
   - Press `Win + I`
   - Or run: `ms-settings:speech`

2. **Navigate to Speech**
   - Go to **Time & Language** > **Speech**

3. **Add Voice**
   - Click **"Add voices"** or **"Manage voices"**
   - Scroll to **"English (United Kingdom)"**

4. **Download Ryan**
   - Find: **"Microsoft Ryan Online (Natural) - English (United Kingdom)"**
   - Click **Download**
   - Wait for completion (may take a few minutes)

5. **Verify**

   ```bash
   python check_voices.py
   ```

   Ryan should now appear in the list.

## Alternative Voices
If Ryan is not available, also good options:
- **Microsoft George** (British gentleman)
- Any **English (United Kingdom)** male voice

## After Installation
Alfred will automatically detect and use Ryan on next startup.

## Current Fallback
Until Ryan is installed, Alfred uses:
1. **Hazel (British female)** - Better British accent than American voices
2. David (American male) - Last resort

Updated voice priority: Ryan > George > British male > British female > American male
