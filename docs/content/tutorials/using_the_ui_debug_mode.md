---
sidebar_position: 8
---

# Using the UI Debug Mode

When you are using xRx, it is sometimes helpful to view the conversational interaction as text instead of purely audio. This tutorial will guide you through setting up and using the built in text debugging feature of the Next.js front end in xRx.

> **Warning**
> This feature is only available when you run the client with `npm run dev` and not via `docker compose` because the docker compose file doesn't pass it to the build context.

The base experience of xRx looks like this:

![xRx Base Experience](/img/ui/xRx_base_experience.png)

In order to see the text transcript of everything you have said to your reasoning agent, you need to define the `NEXT_PUBLIC_UI_DEBUG_MODE` environment variable in your `.env` file. This file should be located at the root of your project.



```bash
# .env
NEXT_PUBLIC_UI_DEBUG_MODE=true
```

You can then run the project with the normal docker compose command:

```bash
docker compose up --build
```

Setting this variable to `true` will enable the ability to toggle between voice and text modes. A new button will appear on the UI like below:

![xRx Debug Experience](/img/ui/xRx_text_debug_experience.png)

Once you click the button, the UI will switch to text mode where you can see the existing conversational history.

![xRx Debug Conversation](/img/ui/xRx_toggle_debug_experience.png)

Happy debugging!