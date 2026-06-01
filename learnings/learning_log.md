# eMFer Learning Log

This file captures raw learnings from building eMFer.

The purpose is to preserve useful insights for future LinkedIn posts, portfolio reflections, and GenAI career transition content.

These notes are not final posts. They should stay simple, specific, and easy to reuse.

---

## Development Learnings

- Streamlit multipage apps can use `st.session_state` to carry context from the home page to later pages.
- If an app has a guided workflow, later pages depending on home page setup is intentional, not necessarily a bug.
- Streamlit pages rerun when navigating through the sidebar. Widgets need stable keys and defaults from `st.session_state` if the app should remember previous selections.
- External APIs can fail by returning an HTML error page instead of JSON. Calling `.json()` directly can crash the app if the API returns something like `502 Bad Gateway`.
- A better user experience is to catch API/network errors and show a friendly Streamlit message instead of exposing a Python traceback.
- Chart-building functions belong in shared modules like `charts.py`, while Streamlit pages should mainly handle user controls, layout, and display.
- When a chart or page becomes reusable, moving it out of the page file makes the project easier to understand and maintain.
- Before calculating rolling returns, the app should check whether the fund has enough NAV history for the selected rolling window.
- Static image assets can be stored in project folders like `assets/brand_logos` and `assets/backgrounds` so the app branding is organized.
- Transparent PNG assets can reduce the visible rectangle effect when placing generated logos on a custom app background.

## GenAI / Agent Learnings

- A coding agent can be guided through a project-level `AGENTS.md` file.
- For learning-focused projects, the agent should act as a tutor and assistant, not as the sole builder.
- Learning capture can be treated as a separate responsibility from code generation, so the project supports both building and career growth.
- Prompt tool rules do not make tools callable by themselves. The model must be wrapped in an agent and explicitly given Python tool functions.
- In LangChain, a tool-calling agent needs three pieces: an LLM, a list of tools, and a prompt that includes an `agent_scratchpad` for the agent's intermediate tool steps.
- The tool output and the user interface output are different things. A chart tool can create a Plotly figure, but Streamlit still needs to display that figure with `st.plotly_chart()`.
- The installed LangChain version matters. Some examples use `create_agent`, but the local environment used `create_tool_calling_agent`, so implementation needs to match the actual package version.
- Generated images are useful for fast brand exploration, but app-ready assets often need cleanup, transparent versions, or simpler variants before they fit the UI.
- Brand assets can be created as a system: full lockup for home/hero, compact logo for app header/sidebar, feature badge for flagship modules, and separate assistant identity for Scout.

## Investing Learnings

- Point-to-point returns can hide how consistently a mutual fund has performed across different market cycles.
- Rolling CAGR helps reveal the range and consistency of investor outcomes across time.
- A fund can look like the best choice at one point in time but lose leadership later. This is a visual reminder that past outperformance does not guarantee future outperformance.
- Fund ranking over time can reveal leadership rotation, decay, comeback, and consistency in a way that a single return table cannot.
- Comparing funds fairly requires matching time horizons and ensuring each fund has enough history for the selected rolling return window.
- Category comparisons can answer practical questions like whether large caps ever beat small caps in a given rolling window, and under what market conditions.

## Product / Founder Learnings

- eMFer is not just a dashboard; it is positioned as a guided research assistant for mutual fund investors.
- Product documentation helps align code, user flow, future roadmap, and AI assistant behavior.
- Keeping the learning log simple makes it more likely to be maintained consistently.
- A feature name can change how a chart feels. "eMFer Funds Marathon" makes the bar chart race feel like a flagship experience instead of a test visualization.
- Product flow matters: Home page selection should lead to individual analysis, then comparison, then the Marathon feature, then Scout for interpretation.
- Visual identity is not only decoration. Logo, page order, feature naming, theme colors, and background graphics together shape how serious and memorable the product feels.
- It is useful to separate the main product brand, flagship feature brand, and AI assistant identity: eMFer, eMFer Funds Marathon, and Scout.
- Dark fintech theming needs careful text contrast, sidebar styling, button states, and background restraint so the app feels premium without hurting readability.
- User review is important for visual design. Screenshots and subjective reactions are valid feedback loops when tuning theme, spacing, and brand feel.

## Cool Ideas

- The funds race idea came while sleeping at night and kept me awake because I started imagining different ways to visualize comparative mutual fund performance in eMFer.
- A bar chart race could make fund comparison feel more alive by showing how leadership changes over time instead of only showing static return tables.
- I want eMFer to explore out-of-the-box investment visualizations. For imagination, the sky is the limit; there is no fixed limit to how beautifully data can be visualized.
- Some ideas may not be common in the investment space yet, but trying them can help eMFer feel more original, engaging, and research-driven.

### eMFer Funds Marathon

- eMFer Funds Marathon can show mutual funds as runners in a long race, where rankings change as rolling returns evolve through time.
- The idea is not just to entertain. It can visually explain that fund leadership is dynamic, and today's winner may not remain the winner across future market cycles.
- One personal example is SBI Small Cap Fund. In 2018, I had picked it as my preferred fund in the small cap space because, at that point, it had very strong 5-year rolling returns and looked promising compared with other small cap funds.
- As time went by, the same fund started slipping in the race: from 1st to 2nd, 3rd, 4th, and eventually toward the lower deciles in the small cap space.
- Seeing that movement visually hit me hard because I had been confident about the fund pick in 2018, but the chart made it obvious how the tides had turned.
- This can become a powerful graphic example of a core investing lesson: past outperformance does not guarantee future outperformance.
- The feature can help investors see performance decay, leadership rotation, consistency, and changing fund rankings more intuitively than a static table.
- It can also make eMFer feel more like an empirical research assistant by turning historical data into a visual story about how fund performance actually behaved over time.
- The tagline for this feature is: "Race Returns. Track Leaders. Stay Ahead."
- The feature badge should feel more energetic than the main eMFer logo, using race lanes, ranked bars, and motion through time.
- The Marathon page should sit after Compare Funds and before Scout, so the user first sees the numbers and charts, then watches the race, then asks Scout for interpretation.
- Plotly animation controls need layout tuning because Play/Pause buttons and sliders can interfere with chart titles, axes, and date labels.
- A race chart should be treated as both analysis and storytelling. It shows who led, who faded, and how the ranking changed through market cycles.

#### Extension Ideas

- Compare funds within the same category, such as small cap, mid cap, large cap, flexi cap, aggressive hybrid, balanced advantage, ELSS, sectoral, or thematic funds, and see which funds kept leadership consistently versus which ones decayed.
- Compare category leaders over time instead of only individual funds: small cap leader vs mid cap leader vs large cap leader vs flexi cap leader.
- Compare global index funds like Nifty 50, Nasdaq 100, S&P 500, Japan index, China index, emerging markets, and gold or commodity-linked funds to see global leadership rotation.
- Cross-compare fund classes, such as small cap vs mid cap vs large cap, and visually test whether the expected risk-return hierarchy actually held across different periods.
- Ask questions like: in a 3-year, 5-year, or 7-year rolling window, has large cap ever beaten small cap? If yes, when, for how long, and during what type of market environment?
- Show leadership decay by tracking how often a fund falls from the top quartile to the middle or bottom quartile over time.
- Show leadership consistency by measuring how long a fund stayed in the top 3, top 5, or top decile of its category.
- Create a "comeback story" view for funds that fell badly but later recovered their ranking.
- Create a "fallen champions" view for funds that once dominated but slowly lost their edge.
- Create a "dark horse" view for funds that started in the middle but steadily climbed into leadership.
- Compare active funds against index funds to see whether active management actually added value over rolling periods.
- Compare fund houses against each other, such as SBI vs HDFC vs ICICI vs Nippon vs Axis, to see which AMC had stronger leadership across categories.
- Compare consistency of categories themselves: which category has more stable leaders, and which category sees constant churn?
- Add drawdown-style race views, where the "winner" is the fund that protected downside best during crashes instead of the one with the highest return.
- Add a risk-adjusted marathon, where funds race on rolling Sharpe ratio, volatility-adjusted returns, or return per unit of risk instead of raw CAGR.
- Add a "regime view" that marks periods like COVID crash, rate hikes, bull runs, corrections, and recovery phases, so the race becomes a story of how funds behaved in different market weather.
- Add a "what I would have believed then vs what happened later" mode, showing how a fund looked at a past decision date and how its rank evolved afterward.
- Use Scout to narrate the marathon: explain why a fund is rising, slipping, recovering, or losing leadership based on the data.
- Turn the race into an investor education tool that breaks free from static table analysis and makes fund behavior feel alive, visual, and memorable.
- Use this as a playground for investment visualization ideas that are more imaginative than the usual one-track analysis of return table, risk table, and final verdict.

## Possible LinkedIn Post Angles

- Why I chose rolling returns instead of simple point-to-point returns for my mutual fund analysis app.
- How I am using AI agents as tutors, not just code generators.
- What building a Streamlit + GenAI project is teaching me about product thinking.
- Why learning logs can become raw material for career transition content.
- How a late-night visualization idea (eMFer Funds Marathon) became a prototype for comparing mutual fund performance over time.
- What a `502 Bad Gateway` taught me about handling real-world API failures in a data app.
- Why a mutual fund analytics tool needs to check fund age before calculating rolling returns.
- How I turned a bar chart race into a flagship product feature instead of leaving it as a test page.
- What designing eMFer taught me about separating product brand, feature brand, and AI assistant identity.
- Why visualizing fund leadership decay can be more powerful than showing a static returns table.
