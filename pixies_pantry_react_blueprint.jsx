// Header Blueprint
import React, { useState } from 'react';
import { ShoppingBag, Menu, X, Search, User, Heart } from 'lucide-react';

const BrandIdentity = ({ isFooter = false }) => {
 const logoUrl = "https://i.imgur.com/vmJPD4c.png";
 const logoUrlAlt = "https://i.imgur.com/Xqc4bAF.png";
 return (
 <div className="flex items-center gap-3">
 <img src={logoUrl} alt="Pixie's Pantry Logo" className={`${isFooter ? 'h-16' : 'h-12'} w-auto object-contain`} onError={(e) => { e.target.src = logoUrlAlt; }} />
 <h1 className={`${isFooter ? 'text-4xl' : 'text-2xl'} font-serif tracking-tight flex items-center leading-none`}>
 <span className="text-pink-400 font-bold">Pixie's</span>
 <span className="text-neutral-300 font-light italic ml-2">Pantry</span>
 </h1>
 </div>
 );
};

const Navbar = ({ cartCount = 0, openCart = () => {} }) => {
 const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
 const navLinks = [
 { label: 'Registry', href: '/registry' },
 { label: 'The Audit', href: '/the-audit' },
 { label: 'Sanctuary', href: '/sanctuary' },
 { label: 'Support', href: '/support' }
 ];
 return (
 // ... (React code stored for translation)
 null
 );
};

// Footer Blueprint
import { Shield, Award } from 'lucide-react';
const Footer = () => {
 return (
 // ... (React code stored for translation)
 null
 );
};
