import React from 'react';
import clsx from 'clsx';
import styles from './styles.module.css';
import { FaBook, FaCode, FaCogs, FaRocket } from 'react-icons/fa';
import useBaseUrl from '@docusaurus/useBaseUrl';

type FeatureItem = {
  title: string;
  icon: React.ReactNode;
  description: JSX.Element;
  link: string;
};

const FeatureList: FeatureItem[] = [
  {
    title: 'Introduction',
    icon: <FaBook />,
    description: <>Get a quick overview of xRx</>,
    link: '/docs/introduction',
  },
  {
    title: 'Tutorials',
    icon: <FaCode />,
    description: <>Find various tutorials for running xRx with different configurations</>,
    link: '/docs/tutorials',
  },
  {
    title: 'How It Works',
    icon: <FaCogs />,
    description: <>Learn about the system architecture and components of xRx</>,
    link: '/docs/category/how-it-works',
  },
  {
    title: 'Demos',
    icon: <FaRocket />,
    description: <>Explore various demos to see xRx in action</>,
    link: '/docs/demos',
  },
];

function Feature({title, icon, description, link}: FeatureItem) {
  const baseUrl = useBaseUrl(link);
  return (
    <div className={clsx('col col--3')}>
      <div className="text--center padding-horiz--md feature-card">
        <div className="feature-icon">{icon}</div>
        <h3>{title}</h3>
        <p>{description}</p>
        <a href={baseUrl} className="button button--primary button--sm">
          Learn More
        </a>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): JSX.Element {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}