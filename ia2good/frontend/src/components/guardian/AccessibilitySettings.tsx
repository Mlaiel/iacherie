import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Slider } from '@/components/ui/slider';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Vibrate, Eye, Volume2, AlertTriangle } from 'lucide-react';

export type HearingLevel = 'deaf' | 'hard_of_hearing' | 'cochlear_implant';

export interface AccessibilitySettings {
  hearing_level: HearingLevel;
  haptic_feedback: boolean;
  visual_alerts: boolean;
  audio_alerts: boolean;
  auto_sos: boolean;
  sos_countdown: number;
  vibration_intensity: number;
  high_visibility_mode: boolean;
  emergency_contacts: EmergencyContact[];
}

export interface EmergencyContact {
  id: string;
  name: string;
  phone: string;
  relationship: string;
}

interface AccessibilitySettingsProps {
  settings: AccessibilitySettings;
  onSettingsChange: (settings: Partial<AccessibilitySettings>) => void;
  onSave: () => void;
}

export const AccessibilitySettingsComponent: React.FC<AccessibilitySettingsProps> = ({
  settings,
  onSettingsChange,
  onSave,
}) => {
  const [testingVibration, setTestingVibration] = useState(false);
  const [newContact, setNewContact] = useState<Partial<EmergencyContact>>({});

  const testVibration = (intensity: number) => {
    if ('vibrate' in navigator) {
      setTestingVibration(true);
      const duration = Math.floor(intensity * 300);
      navigator.vibrate([duration, 100, duration]);
      setTimeout(() => setTestingVibration(false), duration * 2 + 100);
    }
  };

  const testVisualAlert = () => {
    // Create a flash overlay
    const overlay = document.createElement('div');
    overlay.style.cssText = `
      position: fixed;
      inset: 0;
      background: red;
      z-index: 9999;
      animation: flash 0.5s ease-in-out 3;
    `;
    document.body.appendChild(overlay);
    setTimeout(() => document.body.removeChild(overlay), 1500);
  };

  const addEmergencyContact = () => {
    if (newContact.name && newContact.phone) {
      const contact: EmergencyContact = {
        id: Date.now().toString(),
        name: newContact.name,
        phone: newContact.phone,
        relationship: newContact.relationship || 'Other',
      };
      onSettingsChange({
        emergency_contacts: [...settings.emergency_contacts, contact],
      });
      setNewContact({});
    }
  };

  const removeEmergencyContact = (id: string) => {
    onSettingsChange({
      emergency_contacts: settings.emergency_contacts.filter((c) => c.id !== id),
    });
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Hearing Profile */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Volume2 className="w-6 h-6" />
            Profil Auditif
          </CardTitle>
          <CardDescription>
            Configurez votre niveau auditif pour une expérience adaptée
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="hearing-level">Niveau d'audition</Label>
            <Select
              value={settings.hearing_level}
              onValueChange={(value: HearingLevel) =>
                onSettingsChange({ hearing_level: value })
              }
            >
              <SelectTrigger id="hearing-level" className="text-lg">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="deaf">Sourd(e)</SelectItem>
                <SelectItem value="hard_of_hearing">Malentendant(e)</SelectItem>
                <SelectItem value="cochlear_implant">Implant cochléaire</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Alert Preferences */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="w-6 h-6" />
            Préférences d'Alertes
          </CardTitle>
          <CardDescription>
            Choisissez comment vous souhaitez être alerté des dangers
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="haptic-feedback" className="text-lg">
                Retour haptique (vibrations)
              </Label>
              <p className="text-sm text-gray-500">
                Vibrations lors des alertes et interactions
              </p>
            </div>
            <Switch
              id="haptic-feedback"
              checked={settings.haptic_feedback}
              onCheckedChange={(checked) => onSettingsChange({ haptic_feedback: checked })}
            />
          </div>

          {settings.haptic_feedback && (
            <div className="space-y-2 pl-6">
              <Label htmlFor="vibration-intensity">
                Intensité des vibrations: {settings.vibration_intensity}/10
              </Label>
              <div className="flex items-center gap-4">
                <Slider
                  id="vibration-intensity"
                  min={1}
                  max={10}
                  step={1}
                  value={[settings.vibration_intensity]}
                  onValueChange={([value]) =>
                    onSettingsChange({ vibration_intensity: value })
                  }
                  className="flex-1"
                />
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => testVibration(settings.vibration_intensity)}
                  disabled={testingVibration}
                >
                  <Vibrate className="w-4 h-4 mr-2" />
                  Tester
                </Button>
              </div>
            </div>
          )}

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="visual-alerts" className="text-lg">
                Alertes visuelles
              </Label>
              <p className="text-sm text-gray-500">
                Flashs d'écran et notifications visuelles
              </p>
            </div>
            <Switch
              id="visual-alerts"
              checked={settings.visual_alerts}
              onCheckedChange={(checked) => onSettingsChange({ visual_alerts: checked })}
            />
          </div>

          {settings.visual_alerts && (
            <div className="pl-6">
              <Button variant="outline" size="sm" onClick={testVisualAlert}>
                <Eye className="w-4 h-4 mr-2" />
                Tester l'alerte visuelle
              </Button>
            </div>
          )}

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="audio-alerts" className="text-lg">
                Alertes sonores
              </Label>
              <p className="text-sm text-gray-500">
                Sons d'alerte (recommandé pour malentendants)
              </p>
            </div>
            <Switch
              id="audio-alerts"
              checked={settings.audio_alerts}
              onCheckedChange={(checked) => onSettingsChange({ audio_alerts: checked })}
            />
          </div>
        </CardContent>
      </Card>

      {/* SOS Configuration */}
      <Card>
        <CardHeader>
          <CardTitle>Configuration SOS</CardTitle>
          <CardDescription>
            Paramètres du système d'urgence
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="auto-sos" className="text-lg">
                SOS automatique
              </Label>
              <p className="text-sm text-gray-500">
                Déclenchement automatique en cas de chute ou danger détecté
              </p>
            </div>
            <Switch
              id="auto-sos"
              checked={settings.auto_sos}
              onCheckedChange={(checked) => onSettingsChange({ auto_sos: checked })}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="sos-countdown">
              Compte à rebours SOS: {settings.sos_countdown} secondes
            </Label>
            <Slider
              id="sos-countdown"
              min={5}
              max={30}
              step={5}
              value={[settings.sos_countdown]}
              onValueChange={([value]) => onSettingsChange({ sos_countdown: value })}
            />
            <p className="text-sm text-gray-500">
              Temps avant déclenchement automatique du SOS (5-30 secondes)
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Emergency Contacts */}
      <Card>
        <CardHeader>
          <CardTitle>Contacts d'Urgence</CardTitle>
          <CardDescription>
            Maximum 5 contacts qui seront alertés en cas de SOS
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {settings.emergency_contacts.map((contact) => (
            <div
              key={contact.id}
              className="flex items-center justify-between p-4 border rounded-lg"
            >
              <div>
                <p className="font-semibold text-lg">{contact.name}</p>
                <p className="text-sm text-gray-600">{contact.phone}</p>
                <p className="text-xs text-gray-500">{contact.relationship}</p>
              </div>
              <Button
                variant="destructive"
                size="sm"
                onClick={() => removeEmergencyContact(contact.id)}
              >
                Supprimer
              </Button>
            </div>
          ))}

          {settings.emergency_contacts.length < 5 && (
            <div className="space-y-3 p-4 border-2 border-dashed rounded-lg">
              <Input
                placeholder="Nom du contact"
                value={newContact.name || ''}
                onChange={(e) => setNewContact({ ...newContact, name: e.target.value })}
              />
              <Input
                placeholder="Numéro de téléphone"
                type="tel"
                value={newContact.phone || ''}
                onChange={(e) => setNewContact({ ...newContact, phone: e.target.value })}
              />
              <Input
                placeholder="Relation (ex: Mère, Ami, Voisin)"
                value={newContact.relationship || ''}
                onChange={(e) =>
                  setNewContact({ ...newContact, relationship: e.target.value })
                }
              />
              <Button
                onClick={addEmergencyContact}
                disabled={!newContact.name || !newContact.phone}
                className="w-full"
              >
                Ajouter le contact
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* High Visibility Mode */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Eye className="w-6 h-6" />
            Mode Haute Visibilité
          </CardTitle>
          <CardDescription>
            Contraste maximum et éléments agrandis pour meilleure lisibilité
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="high-visibility" className="text-lg">
                Activer le mode haute visibilité
              </Label>
              <p className="text-sm text-gray-500">
                Texte plus grand, contraste élevé, pas d'animations
              </p>
            </div>
            <Switch
              id="high-visibility"
              checked={settings.high_visibility_mode}
              onCheckedChange={(checked) =>
                onSettingsChange({ high_visibility_mode: checked })
              }
            />
          </div>
        </CardContent>
      </Card>

      {/* Save Button */}
      <div className="flex justify-end">
        <Button size="lg" onClick={onSave} className="px-8">
          Enregistrer les paramètres
        </Button>
      </div>
    </div>
  );
};
