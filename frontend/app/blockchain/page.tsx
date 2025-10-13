'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft, Hexagon, Wallet, Image, ShieldCheck, TrendingUp, ExternalLink, Loader2, Copy, Check } from 'lucide-react';

interface BlockchainNetwork {
  id: string;
  name: string;
  chain_id: number;
  rpc_url: string;
  connected: boolean;
  native_token: string;
}

interface NFT {
  id: string;
  token_id: number;
  contract_address: string;
  network: string;
  name: string;
  description: string;
  image_url: string;
  owner: string;
  metadata: any;
  minted_at: string;
}

interface Transaction {
  tx_hash: string;
  from_address: string;
  to_address: string;
  value: number;
  network: string;
  status: 'pending' | 'confirmed' | 'failed';
  block_number?: number;
  timestamp: string;
}

interface WalletInfo {
  address: string;
  balance: number;
  network: string;
  nft_count: number;
}

export default function BlockchainPage() {
  const [networks, setNetworks] = useState<BlockchainNetwork[]>([]);
  const [selectedNetwork, setSelectedNetwork] = useState<string>('ethereum');
  const [wallet, setWallet] = useState<WalletInfo | null>(null);
  const [nfts, setNfts] = useState<NFT[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [mintingNFT, setMintingNFT] = useState(false);
  
  // NFT Minting Form
  const [nftName, setNftName] = useState('');
  const [nftDescription, setNftDescription] = useState('');
  const [nftImage, setNftImage] = useState('');
  
  // Content Registration
  const [contentId, setContentId] = useState('');
  const [registering, setRegistering] = useState(false);

  useEffect(() => {
    fetchData();
  }, [selectedNetwork]);

  const fetchData = async () => {
    try {
      setLoading(true);

      // Fetch blockchain networks
      const networksResponse = await fetch('http://localhost:8000/blockchain/networks');
      if (networksResponse.ok) {
        const data = await networksResponse.json();
        setNetworks(data.networks || []);
      }

      // Fetch wallet info
      const walletResponse = await fetch(`http://localhost:8000/blockchain/wallet?network=${selectedNetwork}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (walletResponse.ok) {
        const data = await walletResponse.json();
        setWallet(data.wallet);
      }

      // Fetch NFTs
      const nftsResponse = await fetch(`http://localhost:8000/blockchain/nfts?network=${selectedNetwork}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (nftsResponse.ok) {
        const data = await nftsResponse.json();
        setNfts(data.nfts || []);
      }

      // Fetch transactions
      const txResponse = await fetch(`http://localhost:8000/blockchain/transactions?network=${selectedNetwork}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (txResponse.ok) {
        const data = await txResponse.json();
        setTransactions(data.transactions || []);
      }
    } catch (error) {
      console.error('Error fetching blockchain data:', error);
    } finally {
      setLoading(false);
    }
  };

  const mintNFT = async () => {
    if (!nftName.trim() || !nftImage.trim()) return;

    try {
      setMintingNFT(true);

      const response = await fetch('http://localhost:8000/blockchain/nft/mint', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          name: nftName,
          description: nftDescription,
          image_url: nftImage,
          network: selectedNetwork,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        alert(`NFT minted successfully! Token ID: ${data.nft.token_id}`);
        setNftName('');
        setNftDescription('');
        setNftImage('');
        fetchData();
      } else {
        const error = await response.json();
        alert(`Minting failed: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error minting NFT:', error);
      alert('Error minting NFT');
    } finally {
      setMintingNFT(false);
    }
  };

  const registerContentRights = async () => {
    if (!contentId.trim()) return;

    try {
      setRegistering(true);

      const response = await fetch('http://localhost:8000/blockchain/content/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          content_id: contentId,
          network: selectedNetwork,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        alert(`Content rights registered! TX: ${data.transaction.tx_hash}`);
        setContentId('');
        fetchData();
      } else {
        alert('Registration failed');
      }
    } catch (error) {
      console.error('Error registering content:', error);
    } finally {
      setRegistering(false);
    }
  };

  const connectWallet = async () => {
    try {
      const response = await fetch('http://localhost:8000/blockchain/wallet/connect', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          network: selectedNetwork,
        }),
      });

      if (response.ok) {
        fetchData();
      }
    } catch (error) {
      console.error('Error connecting wallet:', error);
    }
  };

  const copyAddress = (address: string) => {
    navigator.clipboard.writeText(address);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Header */}
      <div className="bg-white shadow-md border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/" className="text-gray-600 hover:text-indigo-600 transition">
                <ArrowLeft className="h-5 w-5" />
              </Link>
              <Hexagon className="h-8 w-8 text-indigo-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Blockchain Hub</h1>
                <p className="text-sm text-gray-500">NFT Minting • Smart Contracts • Decentralized Rights</p>
              </div>
            </div>
            {wallet && (
              <div className="flex items-center space-x-2 bg-indigo-100 text-indigo-700 px-4 py-2 rounded-lg">
                <Wallet className="h-5 w-5" />
                <span className="font-mono text-sm">
                  {wallet.address.substring(0, 6)}...{wallet.address.substring(wallet.address.length - 4)}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Network Selector */}
        <div className="grid grid-cols-2 md:grid-cols-6 gap-4 mb-8">
          {networks.map((network) => (
            <button
              key={network.id}
              onClick={() => setSelectedNetwork(network.id)}
              className={`p-4 rounded-xl border-2 transition-all transform hover:scale-105 ${
                selectedNetwork === network.id
                  ? 'border-indigo-500 bg-indigo-50 shadow-lg'
                  : 'border-gray-200 bg-white hover:border-gray-300'
              }`}
            >
              <div className="text-center">
                <div className={`w-3 h-3 rounded-full mx-auto mb-2 ${network.connected ? 'bg-green-500' : 'bg-gray-300'}`}></div>
                <div className="font-semibold text-sm text-gray-900">{network.name}</div>
                <div className="text-xs text-gray-500">{network.native_token}</div>
              </div>
            </button>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Wallet Info */}
            {wallet ? (
              <div className="bg-gradient-to-r from-indigo-500 to-purple-500 rounded-xl shadow-lg p-6 text-white">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <div className="text-sm opacity-90 mb-1">Wallet Address</div>
                    <div className="flex items-center space-x-2">
                      <code className="font-mono text-lg">{wallet.address}</code>
                      <button onClick={() => copyAddress(wallet.address)} className="hover:opacity-80">
                        <Copy className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                  <Wallet className="h-12 w-12 opacity-80" />
                </div>
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <div className="text-sm opacity-90">Balance</div>
                    <div className="text-2xl font-bold">{wallet.balance} {networks.find(n => n.id === selectedNetwork)?.native_token}</div>
                  </div>
                  <div>
                    <div className="text-sm opacity-90">Network</div>
                    <div className="text-2xl font-bold">{wallet.network.toUpperCase()}</div>
                  </div>
                  <div>
                    <div className="text-sm opacity-90">NFTs Owned</div>
                    <div className="text-2xl font-bold">{wallet.nft_count}</div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-xl shadow-lg p-8 text-center">
                <Wallet className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-gray-900 mb-2">Connect Your Wallet</h3>
                <p className="text-gray-600 mb-6">Connect your wallet to access blockchain features</p>
                <button
                  onClick={connectWallet}
                  className="bg-indigo-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-indigo-700 transition"
                >
                  Connect Wallet
                </button>
              </div>
            )}

            {/* Mint NFT */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center space-x-3 mb-6">
                <Image className="h-6 w-6 text-purple-600" />
                <h2 className="text-xl font-bold text-gray-900">Mint NFT</h2>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">NFT Name</label>
                  <input
                    type="text"
                    value={nftName}
                    onChange={(e) => setNftName(e.target.value)}
                    placeholder="Enter NFT name..."
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                  <textarea
                    value={nftDescription}
                    onChange={(e) => setNftDescription(e.target.value)}
                    placeholder="Enter NFT description..."
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                    rows={3}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Image URL</label>
                  <input
                    type="url"
                    value={nftImage}
                    onChange={(e) => setNftImage(e.target.value)}
                    placeholder="https://..."
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>

                <button
                  onClick={mintNFT}
                  disabled={!nftName || !nftImage || mintingNFT}
                  className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-4 px-6 rounded-lg font-semibold hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 transition flex items-center justify-center space-x-2"
                >
                  {mintingNFT ? (
                    <>
                      <Loader2 className="h-5 w-5 animate-spin" />
                      <span>Minting...</span>
                    </>
                  ) : (
                    <>
                      <Image className="h-5 w-5" />
                      <span>Mint NFT</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Register Content Rights */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center space-x-3 mb-6">
                <ShieldCheck className="h-6 w-6 text-green-600" />
                <h2 className="text-xl font-bold text-gray-900">Register Content Rights</h2>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Content ID</label>
                  <input
                    type="text"
                    value={contentId}
                    onChange={(e) => setContentId(e.target.value)}
                    placeholder="Enter content ID to register..."
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  />
                </div>

                <button
                  onClick={registerContentRights}
                  disabled={!contentId || registering}
                  className="w-full bg-gradient-to-r from-green-600 to-teal-600 text-white py-4 px-6 rounded-lg font-semibold hover:from-green-700 hover:to-teal-700 disabled:opacity-50 transition flex items-center justify-center space-x-2"
                >
                  {registering ? (
                    <>
                      <Loader2 className="h-5 w-5 animate-spin" />
                      <span>Registering...</span>
                    </>
                  ) : (
                    <>
                      <ShieldCheck className="h-5 w-5" />
                      <span>Register on Blockchain</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* NFT Gallery */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-6">Your NFTs</h2>
              {loading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
                </div>
              ) : nfts.length > 0 ? (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {nfts.map((nft) => (
                    <div key={nft.id} className="border border-gray-200 rounded-lg overflow-hidden hover:shadow-lg transition">
                      <img src={nft.image_url} alt={nft.name} className="w-full h-48 object-cover" />
                      <div className="p-4">
                        <div className="font-semibold text-gray-900 mb-1">{nft.name}</div>
                        <div className="text-sm text-gray-600 mb-2">{nft.description}</div>
                        <div className="flex items-center justify-between text-xs text-gray-500">
                          <span>#{nft.token_id}</span>
                          <span>{nft.network.toUpperCase()}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  No NFTs yet. Mint your first NFT!
                </div>
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            {/* Recent Transactions */}
            <div className="bg-white rounded-xl shadow-lg p-6 sticky top-24">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Recent Transactions</h3>
              {loading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin text-indigo-600" />
                </div>
              ) : transactions.length > 0 ? (
                <div className="space-y-3 max-h-[600px] overflow-y-auto">
                  {transactions.map((tx) => (
                    <div key={tx.tx_hash} className="border border-gray-200 rounded-lg p-3">
                      <div className="flex items-center justify-between mb-2">
                        <div className={`text-xs px-2 py-1 rounded font-medium ${
                          tx.status === 'confirmed' ? 'bg-green-100 text-green-700' :
                          tx.status === 'pending' ? 'bg-yellow-100 text-yellow-700' :
                          'bg-red-100 text-red-700'
                        }`}>
                          {tx.status}
                        </div>
                        <a
                          href={`https://etherscan.io/tx/${tx.tx_hash}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-indigo-600 hover:text-indigo-700"
                        >
                          <ExternalLink className="h-4 w-4" />
                        </a>
                      </div>
                      <div className="text-xs text-gray-600 mb-1">
                        <div className="font-mono truncate">{tx.tx_hash}</div>
                      </div>
                      <div className="flex items-center justify-between text-xs text-gray-500">
                        <span>{tx.value} {networks.find(n => n.id === tx.network)?.native_token}</span>
                        {tx.block_number && <span>Block #{tx.block_number}</span>}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500 text-sm">
                  No transactions yet
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
