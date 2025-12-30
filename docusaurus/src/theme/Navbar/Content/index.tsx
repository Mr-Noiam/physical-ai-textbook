/**
 * Custom Navbar Content
 *
 */

import React, { useState } from 'react';
import {useThemeConfig} from '@docusaurus/theme-common';
import {
  splitNavbarItems,
  useNavbarMobileSidebar,
} from '@docusaurus/theme-common/internal';
import NavbarItem from '@theme/NavbarItem';
import NavbarColorModeToggle from '@theme/Navbar/ColorModeToggle';
import SearchBar from '@theme/SearchBar';
import NavbarMobileSidebarToggle from '@theme/Navbar/MobileSidebar/Toggle';
import NavbarLogo from '@theme/Navbar/Logo';
import NavbarSearch from '@theme/Navbar/Search';
import AuthModal from '@site/src/components/AuthModal';
import { useAuth } from '@site/src/contexts/AuthContext';

import styles from './styles.module.css';

function useNavbarItems() {
  return useThemeConfig().navbar.items;
}

function NavbarItems({items}: {items: any[]}) {
  return (
    <>
      {items.map((item, i) => (
        <NavbarItem {...item} key={i} />
      ))}
    </>
  );
}

function NavbarContentLayout({
  left,
  right,
}: {
  left: React.ReactNode;
  right: React.ReactNode;
}) {
  return (
    <div className="navbar__inner">
      <div className="navbar__items">{left}</div>
      <div className="navbar__items navbar__items--right">
        {right}
      </div>
    </div>
  );
}

export default function NavbarContent(): JSX.Element {
  const mobileSidebar = useNavbarMobileSidebar();
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const { user, signOut: contextSignOut } = useAuth();

  const items = useNavbarItems();
  const [leftItems, rightItems] = splitNavbarItems(items);

  const searchBarItem = items.find((item) => item.type === 'search');

  const handleSignOut = async () => {
    await contextSignOut();
  };

  return (
    <>
      <NavbarContentLayout
        left={
          <>
            {!mobileSidebar.disabled && <NavbarMobileSidebarToggle />}
            <NavbarLogo />
            <NavbarItems items={leftItems} />
          </>
        }
        right={
          <>
            <NavbarItems items={rightItems} />
            <NavbarColorModeToggle className={styles.colorModeToggle} />
            {!searchBarItem && (
              <NavbarSearch>
                <SearchBar />
              </NavbarSearch>
            )}
            {user ? (
              <div className={styles.userMenu}>
                <span className={styles.userName}>{user.name || user.email}</span>
                <button
                  onClick={handleSignOut}
                  className={styles.authButton}
                >
                  Sign Out
                </button>
              </div>
            ) : (
              <button
                onClick={() => setIsAuthModalOpen(true)}
                className={styles.authButton}
              >
                Sign In
              </button>
            )}
          </>
        }
      />
      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
      />
    </>
  );
}
