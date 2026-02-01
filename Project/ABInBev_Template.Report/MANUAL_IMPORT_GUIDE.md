# Power BI Theme Import Guide for ABInBev Template

This guide provides instructions for developers to manually import the ABInBev standard themes into their Power BI Desktop reports. 

> [!IMPORTANT]
> **Theme Update:** The theme files (`ABInBev_Default_Report.json` etc.) have been refined to strictly apply **Core Company Branding** (Color Palette, Font Styles, Visual Styles). They **NO LONGER** contain embedded background images. This ensures a cleaner import process and allows for flexible background management.

## Available Themes

You will find the updated theme files in the `StaticResources\SharedResources\BaseThemes` directory (and `BI-STD\themes`):

1.  **`ABInBev_Default_Report.json`**:
    *   **Use Case:** The primary theme for all ABInBev reports.
    *   **Features:** Applies the standard ABInBev **Color Palette**, **Font Theme** (Segoe UI / Corporate Fonts), and **Visual Container Styles** (rounded corners, standard borders, shadows).
    *   **What's excludes:** No Page Background Images.

## How to Import a Theme in Power BI Desktop

1.  Open your report in **Power BI Desktop**.
2.  Go to the **View** tab in the ribbon.
3.  In the **Themes** gallery, click the dropdown arrow to expand the menu.
4.  Select **Browse for themes**.
5.  Navigate to the theme file location (e.g., `BI-STD\themes\ABInBev_Default_Report.json`).
6.  Select the file and click **Open**.

## Managing Backgrounds Manually

Since the themes no longer force a background image:

1.  **To add a background:**
    *   Go to **Format Pane** > **Canvas background**.
    *   Click **Browse** and select your desired corporate background image (PNG/SVG).
    *   Set **Image fit** to **Fit** or **Fill**.
    *   Set **Transparency** to **0%**.

2.  **Why this approach?**
    *   Reduces JSON file size and complexity.
    *   Prevents accidental background overrides when switching themes.
    *   Allows you to mix and match different layouts (Home Page vs Report Page) while keeping the same core *Data Colors* and *Fonts*.
