import React, { useState, useEffect } from 'react';
import { Activity, Server, Spider, Cpu, CheckCircle, AlertCircle } from 'lucide-react';

/**
 * 🚀 Dashboard Infrastructure - Vue d'ensemble 454 microservices + 13 crawlers
 */
const InfrastructureDashboard = () => {
  const [microservices, setMicroservices] = useState(null);
  const [crawlers, setCrawlers] = useState(null);
  const [platforms, setPlatforms] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadInfrastructure();
  }, []);

  const loadInfrastructure = async () => {
    try {
      // Load microservices
      const msResponse = await fetch('/api/microservices/list');
      const msData = await msResponse.json();
      setMicroservices(msData);

      // Load crawlers
      const crawlersResponse = await fetch('/api/crawlers');
      const crawlersData = await crawlersResponse.json();
      setCrawlers(crawlersData);

      // Load platforms
      const platformsResponse = await fetch('/api/crawlers/platforms/supported');
      const platformsData = await platformsResponse.json();
      setPlatforms(platformsData);

      setLoading(false);
    } catch (error) {
      console.error('Error loading infrastructure:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-gray-900 to-gray-800">
        <div className="text-white text-2xl">
          <Activity className="animate-spin inline-block mr-2" />
          Chargement de l'infrastructure...
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
          🚀 Infrastructure IA Chérie
        </h1>
        <p className="text-gray-400 text-lg">
          454 Microservices • 13+ Crawlers • 11 Plateformes • 53+ AI Agents
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <StatCard
          icon={<Server />}
          title="Microservices"
          value={microservices?.total_services || 0}
          subtitle="services actifs"
          color="blue"
        />
        <StatCard
          icon={<Spider />}
          title="Crawlers"
          value={crawlers?.total_crawlers || 0}
          subtitle="crawlers prêts"
          color="purple"
        />
        <StatCard
          icon={<Activity />}
          title="Plateformes"
          value={platforms?.total_platforms || 0}
          subtitle="réseaux supportés"
          color="green"
        />
        <StatCard
          icon={<Cpu />}
          title="AI Agents"
          value="53+"
          subtitle="agents IA"
          color="orange"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Microservices */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 className="text-2xl font-bold mb-4 flex items-center">
            <Server className="mr-2 text-blue-400" />
            Microservices
          </h2>
          {microservices?.categories && (
            <div className="space-y-3">
              {Object.entries(microservices.categories).map(([key, category]) => (
                <CategoryItem
                  key={key}
                  name={category.name}
                  count={category.count}
                  services={category.services}
                />
              ))}
            </div>
          )}
        </div>

        {/* Crawlers */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 className="text-2xl font-bold mb-4 flex items-center">
            <Spider className="mr-2 text-purple-400" />
            Crawlers
          </h2>
          {crawlers?.crawlers && (
            <div className="space-y-2">
              {Object.entries(crawlers.crawlers).map(([name, type]) => (
                <div key={name} className="flex items-center justify-between p-2 bg-gray-700 rounded">
                  <span className="text-sm">{name}</span>
                  <CheckCircle className="text-green-400 w-4 h-4" />
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Platforms */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 lg:col-span-2">
          <h2 className="text-2xl font-bold mb-4 flex items-center">
            <Activity className="mr-2 text-green-400" />
            Plateformes Supportées
          </h2>
          {platforms?.platforms && (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {platforms.platforms.map((platform) => (
                <PlatformCard key={platform.name} platform={platform} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const StatCard = ({ icon, title, value, subtitle, color }) => {
  const colorClasses = {
    blue: 'from-blue-500 to-blue-600',
    purple: 'from-purple-500 to-purple-600',
    green: 'from-green-500 to-green-600',
    orange: 'from-orange-500 to-orange-600',
  };

  return (
    <div className={`bg-gradient-to-br ${colorClasses[color]} rounded-lg p-6 shadow-lg`}>
      <div className="flex items-center justify-between mb-2">
        <div className="text-white opacity-80">{icon}</div>
        <div className="text-3xl font-bold">{value}</div>
      </div>
      <div className="text-white font-semibold">{title}</div>
      <div className="text-white opacity-70 text-sm">{subtitle}</div>
    </div>
  );
};

const CategoryItem = ({ name, count, services }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="border border-gray-600 rounded-lg overflow-hidden">
      <div
        className="p-3 bg-gray-700 cursor-pointer hover:bg-gray-600 transition-colors flex items-center justify-between"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center">
          <CheckCircle className="text-green-400 w-5 h-5 mr-2" />
          <span className="font-semibold">{name}</span>
        </div>
        <span className="text-gray-400 text-sm">{count} services</span>
      </div>
      {expanded && (
        <div className="p-3 bg-gray-750 space-y-1">
          {services.map((service) => (
            <div key={service.id} className="text-sm text-gray-300 pl-4">
              • {service.name}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const PlatformCard = ({ platform }) => (
  <div className="bg-gray-700 rounded-lg p-4 hover:bg-gray-600 transition-colors">
    <div className="font-semibold mb-2">{platform.name}</div>
    <div className="text-xs text-gray-400 space-y-1">
      {platform.features.slice(0, 2).map((feature, idx) => (
        <div key={idx}>• {feature}</div>
      ))}
    </div>
    <div className="mt-2 text-xs text-green-400">✓ Active</div>
  </div>
);

export default InfrastructureDashboard;
