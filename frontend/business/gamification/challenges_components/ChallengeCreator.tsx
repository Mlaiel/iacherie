/**
 * Challenge Creator - Ultra-Advanced Enterprise System
 * 
 * This component provides comprehensive challenge creation interface with
 * intelligent challenge templates and validation.
 * 
 * Author: Fahed Mlaiel <mlaiel@live.de>
 * Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️  CRITICAL LEGAL NOTICE:
 * This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
 * Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
 * Contact: mlaiel@live.de for licensing inquiries.
 * 
 * 🏆 Expert Development Team Specialties:
 * - Lead AI Developer: Advanced machine learning and AI systems
 * - Backend Senior Engineer: Enterprise Python/FastAPI architecture
 * - ML Engineer: TensorFlow/PyTorch and neural networks
 * - Database Administrator: PostgreSQL and vector databases
 * - Security Specialist: Enterprise security protocols
 * - Microservices Architect: Scalable distributed systems
 * - Audio Engineer: Professional audio processing
 * - DevOps Engineer: CI/CD and cloud infrastructure
 * - AI Prompt Engineer: Advanced prompt engineering
 */

'use client';

import React, { useState } from 'react';
import { ChallengeCreatorData, ChallengeType } from '../types';
import { gamificationStyles } from '../gamification.styles';
import { PlusIcon, SparklesIcon, CheckCircleIcon } from '@heroicons/react/24/outline';
import clsx from 'clsx';

interface ChallengeCreatorProps {
  userId: string;
  className?: string;
  onChallengeCreate?: (challenge: ChallengeCreatorData) => Promise<boolean>;
  onCancel?: () => void;
}

const ChallengeCreator: React.FC<ChallengeCreatorProps> = ({
  userId,
  className,
  onChallengeCreate,
  onCancel
}) => {
  const [formData, setFormData] = useState<ChallengeCreatorData>({
    title: '',
    description: '',
    type: ChallengeType.WEEKLY,
    duration: 7,
    requirements: {},
    rewards: {},
    category: 'content',
    difficulty: 3,
    maxParticipants: undefined
  });
  const [creating, setCreating] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!onChallengeCreate || creating) return;

    try {
      setCreating(true);
      const success = await onChallengeCreate(formData);
      if (success) {
        setSuccess(true);
        setTimeout(() => {
          setSuccess(false);
          setFormData({
            title: '',
            description: '',
            type: ChallengeType.WEEKLY,
            duration: 7,
            requirements: {},
            rewards: {},
            category: 'content',
            difficulty: 3,
            maxParticipants: undefined
          });
        }, 2000);
      }
    } catch (err) {
      console.error('Failed to create challenge:', err);
    } finally {
      setCreating(false);
    }
  };

  if (success) {
    return (
      <div className={clsx(gamificationStyles.container.main, className)}>
        <div className="max-w-2xl mx-auto p-6">
          <div className={gamificationStyles.container.section}>
            <div className="text-center py-12">
              <CheckCircleIcon className="w-16 h-16 text-green-500 mx-auto mb-4" />
              <h2 className={gamificationStyles.typography.heading.secondary}>
                Challenge Created Successfully!
              </h2>
              <p className={gamificationStyles.typography.body.regular}>
                Your challenge has been submitted for review and will be available soon.
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={clsx(gamificationStyles.container.main, className)}>
      <div className="max-w-2xl mx-auto p-6">
        <div className="mb-8">
          <h1 className={clsx(gamificationStyles.typography.heading.primary, "flex items-center")}>
            <PlusIcon className="w-8 h-8 mr-3 text-blue-500" />
            Create Challenge
          </h1>
          <p className={gamificationStyles.typography.body.regular}>
            Design engaging challenges for the creator community
          </p>
        </div>

        <form onSubmit={handleSubmit} className={gamificationStyles.container.section}>
          <div className="space-y-6">
            <div>
              <label className={gamificationStyles.typography.body.regular + " block mb-2"}>
                Challenge Title *
              </label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData((prev: ChallengeCreatorData) => ({ ...prev, title: e.target.value }))}
                placeholder="Enter an engaging challenge title"
                className={gamificationStyles.forms.input}
                required
              />
            </div>

            <div>
              <label className={gamificationStyles.typography.body.regular + " block mb-2"}>
                Description *
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData((prev: ChallengeCreatorData) => ({ ...prev, description: e.target.value }))}
                placeholder="Describe what participants need to do"
                rows={4}
                className={gamificationStyles.forms.textarea}
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className={gamificationStyles.typography.body.regular + " block mb-2"}>
                  Challenge Type *
                </label>
                <select
                  value={formData.type}
                  onChange={(e) => setFormData((prev: ChallengeCreatorData) => ({ ...prev, type: e.target.value as ChallengeType }))}
                  className={gamificationStyles.forms.select}
                >
                  <option value={ChallengeType.DAILY}>Daily</option>
                  <option value={ChallengeType.WEEKLY}>Weekly</option>
                  <option value={ChallengeType.MONTHLY}>Monthly</option>
                  <option value={ChallengeType.SEASONAL}>Seasonal</option>
                  <option value={ChallengeType.SPECIAL}>Special</option>
                </select>
              </div>

              <div>
                <label className={gamificationStyles.typography.body.regular + " block mb-2"}>
                  Duration (days) *
                </label>
                <input
                  type="number"
                  value={formData.duration}
                  onChange={(e) => setFormData((prev: ChallengeCreatorData) => ({ ...prev, duration: parseInt(e.target.value) }))}
                  min="1"
                  max="365"
                  className={gamificationStyles.forms.input}
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className={gamificationStyles.typography.body.regular + " block mb-2"}>
                  Category *
                </label>
                <select
                  value={formData.category}
                  onChange={(e) => setFormData((prev: ChallengeCreatorData) => ({ ...prev, category: e.target.value }))}
                  className={gamificationStyles.forms.select}
                >
                  <option value="content">Content Creation</option>
                  <option value="collaboration">Collaboration</option>
                  <option value="engagement">Engagement</option>
                  <option value="quality">Quality</option>
                  <option value="growth">Growth</option>
                </select>
              </div>

              <div>
                <label className={gamificationStyles.typography.body.regular + " block mb-2"}>
                  Difficulty Level *
                </label>
                <select
                  value={formData.difficulty}
                  onChange={(e) => setFormData((prev: ChallengeCreatorData) => ({ ...prev, difficulty: parseInt(e.target.value) }))}
                  className={gamificationStyles.forms.select}
                >
                  <option value={1}>Beginner</option>
                  <option value={2}>Intermediate</option>
                  <option value={3}>Professional</option>
                  <option value={4}>Expert</option>
                  <option value={5}>Master</option>
                </select>
              </div>
            </div>

            <div>
              <label className={gamificationStyles.typography.body.regular + " block mb-2"}>
                Max Participants (optional)
              </label>
              <input
                type="number"
                value={formData.maxParticipants || ''}
                onChange={(e) => setFormData((prev: ChallengeCreatorData) => ({ 
                  ...prev, 
                  maxParticipants: e.target.value ? parseInt(e.target.value) : undefined 
                }))}
                min="1"
                placeholder="Leave empty for unlimited"
                className={gamificationStyles.forms.input}
              />
            </div>

            <div className="pt-6 border-t border-slate-200 dark:border-slate-700">
              <div className="flex gap-4">
                <button
                  type="submit"
                  disabled={creating || !formData.title || !formData.description}
                  className={clsx(
                    gamificationStyles.buttons.primary,
                    "flex-1",
                    creating && "opacity-50 cursor-not-allowed"
                  )}
                >
                  {creating ? (
                    <>
                      <div className={gamificationStyles.loading.spinner + " mr-2"} />
                      Creating Challenge...
                    </>
                  ) : (
                    <>
                      <SparklesIcon className="w-4 h-4 mr-2" />
                      Create Challenge
                    </>
                  )}
                </button>

                {onCancel && (
                  <button
                    type="button"
                    onClick={onCancel}
                    disabled={creating}
                    className={clsx(gamificationStyles.buttons.ghost, "flex-1")}
                  >
                    Cancel
                  </button>
                )}
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ChallengeCreator;