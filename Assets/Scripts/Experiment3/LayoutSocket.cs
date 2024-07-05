using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.XR.Interaction.Toolkit;

public class LayoutSocket : MonoBehaviour
{
    private XRSocketInteractor interactor;
    private GameObject selectedView;
    void Start()
    {
        interactor = GetComponent<XRSocketInteractor>();
    }

    public void HoldView()
    {
        IXRSelectInteractable obj = interactor.GetOldestInteractableSelected();
        print(obj.transform.name);
        obj.transform.SetParent(transform.parent);
    }
}
