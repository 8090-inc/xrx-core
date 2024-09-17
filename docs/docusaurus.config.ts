import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';
import type {PluginOptions} from '@docusaurus/types';
import { execSync } from 'child_process';

function getCurrentGitBranch(): string {
  try {
    return execSync('git rev-parse --abbrev-ref HEAD').toString().trim();
  } catch (e) {
    console.warn('Failed to get current git branch, falling back to "main"');
    return 'main';
  }
}

const config: Config = {
  title: 'xRx',
  tagline: 'Bring multimodal AI to any application 📱',
  favicon: 'img/base-image.png',

  url: 'https://8090-inc.github.io',
  baseUrl: '/xrx-core/',
  organizationName: '8090-inc',
  projectName: 'xrx-core',

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          path: 'content', 
          sidebarPath: './sidebars.ts',
          editUrl: ({ docPath }) => {
            const branch = getCurrentGitBranch();
            return `https://github.com/8090-inc/xrx-core/blob/${branch}/docs/content/${docPath}`;
          },
        },
        blog: false, // Disable the blog
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  plugins: [
    [
      require.resolve("docusaurus-lunr-search"),
      {
        languages: ["en"],
        indexDocs: true,
        indexBlog: true,
        indexPages: false,
        hashed: true,
      },
    ],
/*[
      'docusaurus-plugin-remote-content',
      {
        // Plugin options
        name: 'remote-docs', // Unique name for this plugin instance
        sourceBaseUrl: 'https://raw.githubusercontent.com/8090-inc/xrx/main/',
        outDir: 'docs/remote', // Local directory to save the downloaded content
        documents: [
          {
            source: 'README.md',
            target: 'README2.md',
          },
          // Add more documents as needed
        ],
        requestConfig: {
          headers: {
            Authorization: `token ${process.env.GITHUB_ACCESS_TOKEN}`,
            Accept: 'application/vnd.github.v3.raw',
          },
        },
      },
    ],*/
  ],

  // add support for mermaid
  markdown: {
    mermaid: true,
  },
  themes: ['@docusaurus/theme-mermaid'],

  themeConfig: {
    // Replace with your project's social card
    image: 'img/base-image.png',
    navbar: {
      title: '',
      logo: {
        alt: 'logo',
        src: 'img/base-image.png',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Documentation',
        },
        /*
        { to: "/blog", label: "Blog", position: "left" },
        */
        {
          href: 'https://github.com/8090-inc/xrx-core',
          label: 'xRx-Core GitHub',
          position: 'right',
        },
        {
          type: 'search',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'Documentation',
              to: 'docs/quickstart',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/8090-inc/xrx-core',
            },
            /*{
              label: 'Discord',
              href: 'https://discord.gg/8090',
            },*/
          ],
        },
        {
          title: 'More',
          items: [
            {
              label: 'Website',
              href: 'https://8090.inc',
            },
          ],
        },
        /*
        {
          title: 'Learn',
          items: [
            {
              label: 'Blog',
              href: 'https://github.com/8090-inc/xrx',
            },
          ],
        },
        */
      ],
      copyright: `Copyright © ${new Date().getFullYear()} xRx`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
    stylesheets: [
      {
        href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap',
        type: 'text/css',
      },
    ],
  } satisfies Preset.ThemeConfig,
};

export default config;