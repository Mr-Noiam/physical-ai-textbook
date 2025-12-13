import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */
const sidebars: SidebarsConfig = {
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Module 1: ROS 2 Fundamentals',
      items: [
        'module-1-ros2/week1-intro',
        'module-1-ros2/week2-fundamentals',
        'module-1-ros2/week3-python',
        'module-1-ros2/week4-urdf',
      ],
    },
    {
      type: 'category',
      label: 'Module 2: Gazebo & Unity Simulation',
      items: [
        'module-2-gazebo/week5-simulation',
        'module-2-gazebo/week6-unity',
      ],
    },
    {
      type: 'category',
      label: 'Module 3: NVIDIA Isaac Platform',
      items: [
        'module-3-isaac/week7-isaac-sim',
        'module-3-isaac/week8-isaac-ros',
        'module-3-isaac/week9-navigation',
      ],
    },
    {
      type: 'category',
      label: 'Module 4: Vision-Language-Action',
      items: [
        'module-4-vla/week10-vla-intro',
        'module-4-vla/week11-voice',
        'module-4-vla/week12-humanoid',
        'module-4-vla/week13-capstone',
      ],
    },
  ],
};

export default sidebars;
