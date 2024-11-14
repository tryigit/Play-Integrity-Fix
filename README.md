# China?
Since all users generally use this module, China Rom developments are integrated into this module. So this module is recommended for Official China Rom.

> [!CAUTION]
> This module permanently removes Magisk 32bit support! The only way to restore 32bit is to reinstall magisk and reinstall other zygisk modules. So, install it with this in mind.

# Diff Versions

## PIFS China
**P**lay **I**ntegrity **F**ix Advanced

New and improved version that passes the Strong test (Includes BL Hiding). Infrastructure by Lsposed developers. Target apps can be customized, does not affect the system. Default to affect all apps.

### PIFS Required
* Android 11+
* Zygisk
* 64bit cpu (armv8a)
* Official Rom (China Recommended)
* Magisk or KernelSU

## PIFB China
**P**lay **I**ntegrity **F**ix Lite

Old and less ram usage method. It does not affect the orther apps in the same way as the PIFS module, only the Google Gsf app hook.

### PIFB Required
* Android 10+
* Zygisk
* 64bit cpu (armv8a)
* Any Rom (China Recommended)
* TEE Supported Device (Not Broken)
* Magisk or KernelSU

> [!WARNING]
> The reason fingerprints/keyboxs inside the module are banned is too many test checks. So do not check unnecessarily.

# Features
+ **Set motherboard to MP**

The phone software detects your device's motherboard as the original motherboard.

+ **Setting the motherboard country to China**

Xiaomi may impose some restrictions on regional roms. Unfortunately, some phones, like the Xiaomi 12T Pro, require additional things like setting the model number. However, this feature is sufficient for models such as Xiaomi 13.

+ **Permanently removing 32bit support for Magisk and modules**

Magisk zygisk will not use ram unnecessarily. Also modules like lsposed.
> [!NOTE]
> Shamiko module is pushing 32bit support and causing an error, report this to the Shamiko developer. Shamiko is excluded for now.

+ **All System Apps Add Magiskhide List**

Disabled by default. You have to manually change the file yourself to use it. You can improve and pull req send, if you want. If you are using custom roms, please do not use this feature.

+ **Zygote 32bit lazyload support for Xiaomi devices**

If you have a good processor, 32bit will use less ram. The basic logic is that zygote32 will not run unnecessarily until a 32bit application is opened. This feature may affect the opening speed of 32bit apps, but who cares?
Also dex2oat 32bit optimization is disabled.

+ **Disable lsposed logs**

Some apps can detect zygisk by reading lsposed logs with getprop. This module prevents this.

+ **Dynamic prop hiding**

If there is a Shamiko module, it does not set props unnecessarily. It allows you to bypass simple bootloader checks if you do not have the Shamiko module.

+ **Advanced bootloader hiding**

You can prevent apps from detecting the bootloader lock. By default all apps, including system apps, are added to the target.txt file.

+ **Prop spoof (PIFB)**

Droidguard reads info like fingerprint and device model differently. So hook. File is not set as default.

+ **BL certificate spoof**

The *PIFB version* only affects the gms app. It is simple and old.
The *PIFS version* only affects target.txt apps and can be customized. Includes various advanced stuff.
*Both versions* randomly replace a Keybox file to avoid detection and replace it again on reboot.

## Test fp/keybox without needing to reboot
```
su -c killall com.google.android.gms.unstable
```

## Fingerprint File (PIFB)
in device
```
/data/adb/pif.json
```
## Targer File (PIFS)
```
/data/adb/tricky_store/target.txt
```
> [!NOTE]
> If you want to customize it, remove this file because it will be overwritten after every reboot.
```
/data/adb/tricky_store/AllAppsTarget.sh
```
## Keybox File
in device

**PIFB:**
```
/data/adb/keybox.xml
```
**PIFS:**
```
/data/adb/tricky_store/keybox.xml
```
**Simple Strong Guide:**
in maintenance.

## All Target Setting (PIFS)
Add all apps to the target.txt list automatically. It is enabled by default and needs to be removed to customize.

```
/data/adb/tricky_store/AllAppsTarget.sh
```

## Advanced Settings
Add system apps to the Magiskhide list automatically (Currently Development). Move to file paths to active it. 
> [!WARNING]
> There will be incompatibility with modules that modify system files such as GPU Driver. That is why it is not the default.

**PIFB:**
```
/data/adb/SystemAppAdd.sh
```
**PIFS**
```
/data/adb/tricky_store/AllTargetMagiskhide.sh
```

## Motherboard Check
The factory location information on your phone's motherboard.
```
getprop ro.boot.hwc
```

## Telegram
https://t.me/cleverestech

> [!NOTE]
> I do not share my own projects on github (This project is only for update) So this is a fork. You can see whose project I forked in the changelog.

These are just things I make and use myself and I share them because people want them, so I don't look at the issues much and I don't waste my time. It's not worth it.
