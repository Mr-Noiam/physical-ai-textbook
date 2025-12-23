/**
 * User Profile Page
 */

import React from 'react';
import Layout from '@theme/Layout';
import UserProfile from '@site/src/components/UserProfile';

export default function ProfilePage(): JSX.Element {
  return (
    <Layout
      title="Profile"
      description="Manage your profile and personalization settings">
      <UserProfile />
    </Layout>
  );
}
